from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import hashlib
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui_123456'
CORS(app)

# Configuración de la base de datos
DB_CONFIG = {
    'dbname': 'sistema_app_denuncias',
    'user': 'DarkLight',  # Cambia según tu usuario
    'password': 'Zeus9119',  # Cambia según tu contraseña
    'host': 'localhost',
    'port': '5432'
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)

# ==================== RUTAS PRINCIPALES ====================

@app.route('/')

def index():

    return render_template('index.html')

# ==================== AUTENTICACIÓN ====================

@app.route('/api/login', methods=['POST'])

def login():
    
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    # Hash simple (en producción usar bcrypt)
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, username, rol FROM usuarios WHERE username = %s AND password = %s", 
                (username, password_hash))
    user = cur.fetchone()
    cur.close()
    conn.close()
    
    if user:
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['rol'] = user['rol']
        return jsonify({'success': True, 'user': user})
    else:
        return jsonify({'success': False, 'message': 'Usuario o contraseña incorrectos'})

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/registro', methods=['POST'])
def registro():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO usuarios (username, password, email, rol) VALUES (%s, %s, %s, 'usuario')",
                    (username, password_hash, email))
        conn.commit()
        return jsonify({'success': True, 'message': 'Usuario registrado exitosamente'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cur.close()
        conn.close()

@app.route('/api/session', methods=['GET'])
def get_session():
    if 'user_id' in session:
        return jsonify({
            'logged_in': True,
            'username': session.get('username'),
            'rol': session.get('rol')
        })
    return jsonify({'logged_in': False})

# ==================== INVENTARIO ====================

@app.route('/api/productos', methods=['GET'])
def get_productos():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM productos ORDER BY id")
    productos = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(productos)

@app.route('/api/productos', methods=['POST'])
def create_producto():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO productos (codigo, nombre, descripcion, categoria, precio_compra, precio_venta, stock_actual, stock_minimo, unidad_medida, ubicacion)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (data['codigo'], data['nombre'], data.get('descripcion', ''),
              data.get('categoria', ''), data.get('precio_compra', 0),
              data.get('precio_venta', 0), data.get('stock_actual', 0),
              data.get('stock_minimo', 5), data.get('unidad_medida', 'unidad'),
              data.get('ubicacion', '')))
        
        producto_id = cur.fetchone()['id']
        conn.commit()
        return jsonify({'success': True, 'id': producto_id})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cur.close()
        conn.close()

@app.route('/api/productos/<int:producto_id>', methods=['PUT'])
def update_producto(producto_id):
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            UPDATE productos 
            SET codigo=%s, nombre=%s, descripcion=%s, categoria=%s, 
                precio_compra=%s, precio_venta=%s, stock_actual=%s, 
                stock_minimo=%s, unidad_medida=%s, ubicacion=%s
            WHERE id=%s
        """, (data['codigo'], data['nombre'], data.get('descripcion', ''),
              data.get('categoria', ''), data.get('precio_compra', 0),
              data.get('precio_venta', 0), data.get('stock_actual', 0),
              data.get('stock_minimo', 5), data.get('unidad_medida', 'unidad'),
              data.get('ubicacion', ''), producto_id))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cur.close()
        conn.close()

@app.route('/api/productos/<int:producto_id>', methods=['DELETE'])
def delete_producto(producto_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("DELETE FROM productos WHERE id=%s", (producto_id,))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cur.close()
        conn.close()

@app.route('/api/movimientos', methods=['POST'])
def registrar_movimiento():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Obtener stock actual
        cur.execute("SELECT stock_actual FROM productos WHERE id=%s", (data['producto_id'],))
        stock_actual = cur.fetchone()['stock_actual']
        
        stock_nuevo = stock_actual
        if data['tipo'] == 'entrada':
            stock_nuevo = stock_actual + data['cantidad']
        elif data['tipo'] == 'salida':
            stock_nuevo = stock_actual - data['cantidad']
        elif data['tipo'] == 'ajuste':
            stock_nuevo = data['cantidad']
        
        # Registrar movimiento
        cur.execute("""
            INSERT INTO movimientos (producto_id, tipo_movimiento, cantidad, stock_anterior, stock_nuevo, motivo, usuario_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (data['producto_id'], data['tipo'], data['cantidad'], stock_actual, stock_nuevo,
              data.get('motivo', ''), session.get('user_id')))
        
        # Actualizar stock
        cur.execute("UPDATE productos SET stock_actual=%s WHERE id=%s", (stock_nuevo, data['producto_id']))
        
        conn.commit()
        return jsonify({'success': True, 'stock_nuevo': stock_nuevo})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cur.close()
        conn.close()

@app.route('/api/movimientos/<int:producto_id>', methods=['GET'])
def get_movimientos(producto_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT m.*, u.username 
        FROM movimientos m
        LEFT JOIN usuarios u ON m.usuario_id = u.id
        WHERE m.producto_id = %s
        ORDER BY m.fecha_movimiento DESC
        LIMIT 50
    """, (producto_id,))
    movimientos = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(movimientos)

# ==================== DENUNCIAS ====================

@app.route('/api/denuncias', methods=['GET'])
def get_denuncias():
    estado = request.args.get('estado', 'todos')
    conn = get_db_connection()
    cur = conn.cursor()
    
    if estado == 'todos':
        cur.execute("""
            SELECT d.*, u.username 
            FROM denuncias d
            JOIN usuarios u ON d.usuario_id = u.id
            ORDER BY d.fecha_denuncia DESC
        """)
    else:
        cur.execute("""
            SELECT d.*, u.username 
            FROM denuncias d
            JOIN usuarios u ON d.usuario_id = u.id
            WHERE d.estado = %s
            ORDER BY d.fecha_denuncia DESC
        """, (estado,))
    
    denuncias = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(denuncias)

@app.route('/api/denuncias', methods=['POST'])
def create_denuncia():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO denuncias (titulo, contenido, categoria, ubicacion, evidencia_url, estado, usuario_id)
            VALUES (%s, %s, %s, %s, %s, 'pendiente', %s)
            RETURNING id
        """, (data['titulo'], data['contenido'], data.get('categoria', ''),
              data.get('ubicacion', ''), data.get('evidencia_url', ''), session.get('user_id')))
        
        denuncia_id = cur.fetchone()['id']
        conn.commit()
        return jsonify({'success': True, 'id': denuncia_id})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cur.close()
        conn.close()

@app.route('/api/denuncias/<int:denuncia_id>', methods=['PUT'])
def update_denuncia(denuncia_id):
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            UPDATE denuncias 
            SET estado=%s, resolucion=%s, fecha_resolucion=CURRENT_TIMESTAMP
            WHERE id=%s
        """, (data['estado'], data.get('resolucion', ''), denuncia_id))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cur.close()
        conn.close()

@app.route('/api/denuncias/<int:denuncia_id>/comentarios', methods=['GET'])
def get_comentarios(denuncia_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.*, u.username 
        FROM comentarios_denuncias c
        JOIN usuarios u ON c.usuario_id = u.id
        WHERE c.denuncia_id = %s
        ORDER BY c.fecha_comentario ASC
    """, (denuncia_id,))
    comentarios = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(comentarios)

@app.route('/api/denuncias/<int:denuncia_id>/comentarios', methods=['POST'])
def add_comentario(denuncia_id):
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO comentarios_denuncias (denuncia_id, usuario_id, comentario)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (denuncia_id, session.get('user_id'), data['comentario']))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)})
    finally:
        cur.close()
        conn.close()

# ==================== DASHBOARD ====================

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Estadísticas de inventario
    cur.execute("SELECT COUNT(*) as total_productos, SUM(stock_actual) as stock_total FROM productos")
    inventario_stats = cur.fetchone()
    
    # Productos con bajo stock
    cur.execute("SELECT COUNT(*) as bajo_stock FROM productos WHERE stock_actual <= stock_minimo")
    bajo_stock = cur.fetchone()
    
    # Estadísticas de denuncias
    cur.execute("""
        SELECT 
            COUNT(*) as total_denuncias,
            SUM(CASE WHEN estado='pendiente' THEN 1 ELSE 0 END) as pendientes,
            SUM(CASE WHEN estado='aprobada' THEN 1 ELSE 0 END) as aprobadas,
            SUM(CASE WHEN estado='rechazada' THEN 1 ELSE 0 END) as rechazadas
        FROM denuncias
    """)
    denuncias_stats = cur.fetchone()
    
    cur.close()
    conn.close()
    
    return jsonify({
        'inventario': inventario_stats,
        'bajo_stock': bajo_stock,
        'denuncias': denuncias_stats
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)