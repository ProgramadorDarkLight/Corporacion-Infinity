"""
SISTEMA DE INVENTARIOS INFINITY 8 CORP 2026
=============================================
Versión: 8.0 Cyber Edicion
Autor: Ingeniero Alejandro - INFINITY CORP
Estilo: Paleta cibernética - Ámbar/Dorado y Azules
"""

# ============================================
# IMPORTACIÓN DE MÓDULOS
# ============================================
import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
from datetime import datetime
import os

# ============================================
# PALETA DE COLORES CIBERNÉTICA
# ============================================
class CyberColors:
    """
    Paleta de colores inspirada en temas cibernéticos
    Combinación de ámbar/dorado con azules neón
    """
    # Colores principales
    DORADO_PRINCIPAL = "#FFB347"      # Ámbar/Dorado cálido
    DORADO_OSCURO = "#CC8B3C"          # Dorado más profundo
    AZUL_NEON = "#00B4FF"              # Azul eléctrico/cibernético
    AZUL_PROFUNDO = "#005F8C"          # Azul marino profundo
    AZUL_OSCURO = "#003153"            # Azul medianoche
    
    # Colores de fondo
    FONDO_PRINCIPAL = "#0A0E1A"        # Casi negro con tintes azules
    FONDO_SECUNDARIO = "#121827"       # Gris muy oscuro azulado
    FONDO_DESTACADO = "#1E2639"        # Para elementos destacados
    
    # Colores de texto
    TEXTO_PRINCIPAL = "#FFFFFF"        # Blanco puro
    TEXTO_SECUNDARIO = "#B0BEC5"       # Gris claro
    TEXTO_DORADO = "#FFB347"            # Dorado para acentos
    TEXTO_AZUL = "#00B4FF"              # Azul neón para acentos
    
    # Colores de botones
    BOTON_AGREGAR = "#00B4FF"           # Azul neón
    BOTON_EDITAR = "#FFB347"            # Dorado
    BOTON_ELIMINAR = "#FF4C4C"          # Rojo coral (para alertas)
    BOTON_COMPRAR = "#4CAF50"           # Verde (éxito)
    BOTON_VENDER = "#FF9800"            # Naranja (acción)
    BOTON_BALANCE = "#9C27B0"           # Púrpura (especial)
    BOTON_ACTUALIZAR = "#2196F3"        # Azul (refrescar)
    
    # Bordes y efectos
    BORDE_NEON = "#00B4FF"              # Borde con efecto neón
    SOMBRA = "#000000"                   # Sombra negra

# ============================================
# CONFIGURACIÓN DE BASE DE DATOS
# ============================================
class Config:
    """Configuración centralizada de la aplicación"""
    
    # Configuración de desarrollo
    DB_NAME = "inventario8Corp"
    DB_USER = "DarkLight"
    DB_PASSWORD = "Zeus9119*"
    DB_HOST = "localhost"
    DB_PORT = "5432"
    DB_SCHEMA = "inventario8Corp"
    
    @classmethod
    def get_config(cls):
        """Obtiene configuración con soporte para variables de entorno"""
        return {
            'dbname': os.environ.get('DB_NAME', cls.DB_NAME),
            'user': os.environ.get('DB_USER', cls.DB_USER),
            'password': os.environ.get('DB_PASSWORD', cls.DB_PASSWORD),
            'host': os.environ.get('DB_HOST', cls.DB_HOST),
            'port': os.environ.get('DB_PORT', cls.DB_PORT),
            'schema': os.environ.get('DB_SCHEMA', cls.DB_SCHEMA)
        }

# ============================================
# CONEXIÓN A BASE DE DATOS
# ============================================
class ConexionDB:
    """Gestor de conexión a PostgreSQL"""
    
    def __init__(self):
        """Inicializa la conexión a la base de datos"""
        config = Config.get_config()
        
        try:
            # Establece conexión con PostgreSQL
            self.conn = psycopg2.connect(
                dbname=config['dbname'],
                user=config['user'],
                password=config['password'],
                host=config['host'],
                port=config['port']
            )
            
            # Crea cursor para ejecutar consultas
            self.cur = self.conn.cursor()
            
            # Configura el esquema de trabajo
            self.cur.execute('SET search_path TO "{}", public'.format(config['schema']))
            self.conn.commit()
            
            # Verificar y crear columna codigo_barras si no existe
            self.verificar_columna_codigo_barras()
            
            print("✅ Conexión a la base de datos establecida")
            print(f"📁 Esquema configurado: {config['schema']}")
            
        except Exception as e:
            print(f"❌ Error al conectar: {e}")
            self.conn = None
            self.cur = None

    def verificar_columna_codigo_barras(self):
        """Verifica si existe la columna codigo_barras y la crea si no existe"""
        try:
            # Verificar si la columna existe
            self.cur.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='productos' AND column_name='codigo_barras'
            """)
            
            if not self.cur.fetchone():
                print("📦 Agregando columna 'codigo_barras' a la tabla productos...")
                self.cur.execute("""
                    ALTER TABLE productos 
                    ADD COLUMN codigo_barras VARCHAR(50) UNIQUE
                """)
                self.conn.commit()
                print("✅ Columna 'codigo_barras' agregada exitosamente")
            else:
                print("✓ La columna 'codigo_barras' ya existe")
                
        except Exception as e:
            print(f"⚠️ Error al verificar/crear columna codigo_barras: {e}")
            self.conn.rollback()

    def close(self):
        """Cierra la conexión a la base de datos"""
        try:
            if self.cur:
                self.cur.close()
            if self.conn:
                self.conn.close()
                print("🔌 Conexión a la base de datos cerrada")
        except Exception as e:
            print(f"⚠️ Error al cerrar la conexión: {e}")

# ============================================
# FUNCIONES DE VALIDACIÓN
# ============================================
def validar_numero(valor, tipo='int', mensaje="valor"):
    """
    Valida que un valor sea numérico
    
    Args:
        valor: Valor a validar
        tipo: 'int' o 'float'
        mensaje: Nombre del campo para mensaje de error
    
    Returns:
        int o float: Valor convertido
    """
    try:
        if tipo == 'int':
            return int(valor)
        else:
            return float(valor)
    except ValueError:
        raise ValueError(f"❌ El {mensaje} debe ser un número válido")

def validar_texto_no_vacio(texto, campo="Campo"):
    """
    Valida que un texto no esté vacío
    
    Args:
        texto: Texto a validar
        campo: Nombre del campo
    
    Returns:
        str: Texto limpio
    """
    if not texto or not texto.strip():
        raise ValueError(f"❌ {campo} no puede estar vacío")
    return texto.strip()

def centrar_ventana(ventana, ancho, alto):
    """Centra una ventana en la pantalla"""
    pantalla_ancho = ventana.winfo_screenwidth()
    pantalla_alto = ventana.winfo_screenheight()
    x = (pantalla_ancho - ancho) // 2
    y = (pantalla_alto - alto) // 2
    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

# ============================================
# FUNCIONES CRUD
# ============================================
def obtener_productos(busqueda=""):
    """
    Obtiene productos de la base de datos
    
    Args:
        busqueda: Texto para filtrar
    
    Returns:
        list: Lista de productos
    """
    if not db.cur:
        print("❌ Conexión no establecida")
        return []
    
    try:
        # Consulta base incluyendo código de barras
        query = "SELECT id, nombre, descripcion, precio, stock, codigo_barras FROM productos"
        params = []
        
        # Agrega filtro si hay búsqueda
        if busqueda:
            query += " WHERE nombre ILIKE %s OR descripcion ILIKE %s OR codigo_barras ILIKE %s"
            params = [f'%{busqueda}%', f'%{busqueda}%', f'%{busqueda}%']
            db.cur.execute(query, params)
        else:
            db.cur.execute(query + " ORDER BY id")
            
        return db.cur.fetchall()
        
    except Exception as e:
        print(f"❌ Error al obtener productos: {e}")
        return []

def cargar_productos(busqueda=""):
    """Carga productos en el TreeView"""
    # Limpia el TreeView
    for item in treeview_productos.get_children():
        treeview_productos.delete(item)
    
    # Obtiene productos
    productos = obtener_productos(busqueda)
    
    # Inserta productos en el TreeView
    for producto in productos:
        valores = list(producto)
        if len(valores) >= 4:
            valores[3] = f"${valores[3]:.2f}"  # Formatea precio
        treeview_productos.insert("", "end", values=valores)
    
    # Actualiza contador
    actualizar_contador()

def buscar_producto(event=None):
    """Búsqueda en tiempo real"""
    busqueda = entry_buscar.get()
    cargar_productos(busqueda)

def crear_boton_estilizado(parent, texto, comando, color_fondo, ancho=15):
    """
    Crea un botón con estilo personalizado
    
    Args:
        parent: Widget padre
        texto: Texto del botón
        comando: Función a ejecutar
        color_fondo: Color de fondo
        ancho: Ancho del botón en caracteres
    
    Returns:
        tk.Button: Botón creado
    """
    btn = tk.Button(
        parent,
        text=texto,
        command=comando,
        bg=color_fondo,
        fg=CyberColors.TEXTO_PRINCIPAL,
        font=("Segoe UI", 10, "bold"),
        padx=15,
        pady=8,
        relief="flat",
        cursor="hand2",
        width=ancho,
        bd=0,
        highlightthickness=1,
        highlightbackground=CyberColors.BORDE_NEON,
        highlightcolor=CyberColors.BORDE_NEON,
        activebackground=color_fondo,
        activeforeground=CyberColors.TEXTO_PRINCIPAL
    )
    
    # Efecto hover
    def on_enter(e):
        btn['background'] = color_fondo + 'dd'
        
    def on_leave(e):
        btn['background'] = color_fondo
    
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    
    return btn

def eliminar_producto():
    """Elimina el producto seleccionado"""
    try:
        # Verifica selección
        selected = treeview_productos.selection()
        if not selected:
            messagebox.showwarning("⚠️ Advertencia", "Seleccione un producto")
            return
        
        # Confirmación con estilo
        if not messagebox.askyesno(
            "⚠️ CONFIRMAR ELIMINACIÓN",
            "¿Eliminar producto permanentemente?\nEsta acción no se puede deshacer."
        ):
            return
        
        # Obtiene ID y elimina
        producto_id = treeview_productos.item(selected[0])['values'][0]
        db.cur.execute("DELETE FROM productos WHERE id = %s", (producto_id,))
        db.conn.commit()
        
        messagebox.showinfo("✅ Éxito", "Producto eliminado")
        cargar_productos()
        
    except Exception as e:
        db.conn.rollback()
        messagebox.showerror("❌ Error", f"No se pudo eliminar: {e}")

def agregar_producto():
    """Abre ventana para agregar producto"""
    ventana_agregar = tk.Toplevel(ventana)
    ventana_agregar.title("➕ AGREGAR PRODUCTO - CYBER INVENTORY")
    ventana_agregar.geometry("500x600")
    ventana_agregar.configure(bg=CyberColors.FONDO_PRINCIPAL)
    ventana_agregar.transient(ventana)
    ventana_agregar.grab_set()
    
    centrar_ventana(ventana_agregar, 500, 600)
    
    # Título
    titulo = tk.Label(
        ventana_agregar,
        text="➕ NUEVO PRODUCTO",
        font=("Segoe UI", 16, "bold"),
        bg=CyberColors.FONDO_PRINCIPAL,
        fg=CyberColors.TEXTO_DORADO
    )
    titulo.pack(pady=20)
    
    # Frame para el formulario
    form_frame = tk.Frame(ventana_agregar, bg=CyberColors.FONDO_SECUNDARIO, padx=30, pady=20)
    form_frame.pack(fill="both", padx=30, pady=10)
    
    # Crear campos del formulario
    labels = ["Nombre:", "Descripción:", "Precio ($):", "Stock (unidades):", "Código de Barras:"]
    entries = []
    
    for i, label_text in enumerate(labels):
        label = tk.Label(
            form_frame,
            text=label_text,
            font=("Segoe UI", 10),
            bg=CyberColors.FONDO_SECUNDARIO,
            fg=CyberColors.TEXTO_AZUL
        )
        label.pack(pady=(10, 0))
        
        entry = tk.Entry(
            form_frame,
            font=("Segoe UI", 10),
            width=40,
            bg=CyberColors.FONDO_DESTACADO,
            fg=CyberColors.TEXTO_PRINCIPAL,
            insertbackground=CyberColors.TEXTO_DORADO,
            relief="flat",
            bd=2
        )
        entry.pack(pady=5, padx=20)
        entries.append(entry)
    
    entry_nombre, entry_descripcion, entry_precio, entry_stock, entry_codigo_barras = entries
    
    def guardar_producto():
        """Guarda el producto en la base de datos"""
        try:
            # Validaciones
            nombre = validar_texto_no_vacio(entry_nombre.get(), "Nombre")
            descripcion = entry_descripcion.get() or "Sin descripción"
            precio = validar_numero(entry_precio.get(), 'float', 'precio')
            stock = validar_numero(entry_stock.get(), 'int', 'stock')
            codigo_barras = entry_codigo_barras.get().strip() or None
            
            if precio <= 0:
                raise ValueError("❌ El precio debe ser mayor a 0")
            if stock < 0:
                raise ValueError("❌ El stock no puede ser negativo")
            
            # Verificar si el código de barras ya existe
            if codigo_barras:
                db.cur.execute("SELECT id FROM productos WHERE codigo_barras = %s", (codigo_barras,))
                if db.cur.fetchone():
                    raise ValueError("❌ El código de barras ya existe")
            
            # Inserta en BD
            db.cur.execute("""
                INSERT INTO productos (nombre, descripcion, precio, stock, codigo_barras) 
                VALUES (%s, %s, %s, %s, %s)
            """, (nombre, descripcion, precio, stock, codigo_barras))
            
            db.conn.commit()
            messagebox.showinfo("✅ Éxito", "Producto agregado correctamente")
            cargar_productos()
            ventana_agregar.destroy()
            
        except ValueError as e:
            messagebox.showerror("❌ Error de validación", str(e))
        except Exception as e:
            db.conn.rollback()
            messagebox.showerror("❌ Error", f"No se pudo agregar: {e}")
    
    # Frame para botones
    btn_frame = tk.Frame(ventana_agregar, bg=CyberColors.FONDO_PRINCIPAL)
    btn_frame.pack(pady=20)
    
    # Botón guardar
    btn_guardar = crear_boton_estilizado(
        btn_frame,
        "💾 GUARDAR PRODUCTO",
        guardar_producto,
        CyberColors.BOTON_AGREGAR,
        ancho=20
    )
    btn_guardar.pack(side="left", padx=10)
    
    # Botón cancelar
    btn_cancelar = crear_boton_estilizado(
        btn_frame,
        "❌ CANCELAR",
        ventana_agregar.destroy,
        CyberColors.BOTON_ELIMINAR,
        ancho=15
    )
    btn_cancelar.pack(side="left", padx=10)

def actualizar_producto():
    """Abre ventana para actualizar producto"""
    try:
        # Verifica selección
        selected = treeview_productos.selection()
        if not selected:
            messagebox.showwarning("⚠️ Advertencia", "Seleccione un producto")
            return
        
        # Obtiene datos actuales
        valores = treeview_productos.item(selected[0])['values']
        producto_id = valores[0]
        nombre_actual = valores[1]
        descripcion_actual = valores[2]
        precio_actual = valores[3].replace('$', '') if isinstance(valores[3], str) else valores[3]
        stock_actual = valores[4]
        codigo_barras_actual = valores[5] if len(valores) > 5 else ""
        
        # Crear ventana de actualización
        ventana_actualizar = tk.Toplevel(ventana)
        ventana_actualizar.title("✏️ ACTUALIZAR PRODUCTO - CYBER INVENTORY")
        ventana_actualizar.geometry("500x650")
        ventana_actualizar.configure(bg=CyberColors.FONDO_PRINCIPAL)
        ventana_actualizar.transient(ventana)
        ventana_actualizar.grab_set()
        
        centrar_ventana(ventana_actualizar, 500, 650)
        
        # Título
        titulo = tk.Label(
            ventana_actualizar,
            text="✏️ ACTUALIZAR PRODUCTO",
            font=("Segoe UI", 16, "bold"),
            bg=CyberColors.FONDO_PRINCIPAL,
            fg=CyberColors.TEXTO_DORADO
        )
        titulo.pack(pady=20)
        
        # ID del producto
        id_frame = tk.Frame(ventana_actualizar, bg=CyberColors.FONDO_SECUNDARIO)
        id_frame.pack(padx=30, pady=5, fill="x")
        
        tk.Label(
            id_frame,
            text=f"ID Producto: {producto_id}",
            font=("Segoe UI", 11, "bold"),
            bg=CyberColors.FONDO_SECUNDARIO,
            fg=CyberColors.TEXTO_AZUL
        ).pack(pady=5)
        
        # Frame para el formulario
        form_frame = tk.Frame(ventana_actualizar, bg=CyberColors.FONDO_SECUNDARIO, padx=30, pady=20)
        form_frame.pack(fill="both", padx=30, pady=10)
        
        # Crear campos
        labels = ["Nombre:", "Descripción:", "Precio ($):", "Stock (unidades):", "Código de Barras:"]
        entries = []
        valores_actuales = [nombre_actual, descripcion_actual, precio_actual, stock_actual, codigo_barras_actual]
        
        for i, label_text in enumerate(labels):
            label = tk.Label(
                form_frame,
                text=label_text,
                font=("Segoe UI", 10),
                bg=CyberColors.FONDO_SECUNDARIO,
                fg=CyberColors.TEXTO_AZUL
            )
            label.pack(pady=(10, 0))
            
            entry = tk.Entry(
                form_frame,
                font=("Segoe UI", 10),
                width=40,
                bg=CyberColors.FONDO_DESTACADO,
                fg=CyberColors.TEXTO_PRINCIPAL,
                insertbackground=CyberColors.TEXTO_DORADO,
                relief="flat",
                bd=2
            )
            entry.insert(0, str(valores_actuales[i]))
            entry.pack(pady=5, padx=20)
            entries.append(entry)
        
        entry_nombre, entry_descripcion, entry_precio, entry_stock, entry_codigo_barras = entries
        
        def guardar_cambios():
            """Guarda los cambios en BD"""
            try:
                nombre = validar_texto_no_vacio(entry_nombre.get(), "Nombre")
                descripcion = entry_descripcion.get() or "Sin descripción"
                precio = validar_numero(entry_precio.get(), 'float', 'precio')
                stock = validar_numero(entry_stock.get(), 'int', 'stock')
                codigo_barras = entry_codigo_barras.get().strip() or None
                
                if precio <= 0:
                    raise ValueError("❌ El precio debe ser mayor a 0")
                if stock < 0:
                    raise ValueError("❌ El stock no puede ser negativo")
                
                # Verificar si el código de barras ya existe (excepto para este producto)
                if codigo_barras:
                    db.cur.execute(
                        "SELECT id FROM productos WHERE codigo_barras = %s AND id != %s", 
                        (codigo_barras, producto_id)
                    )
                    if db.cur.fetchone():
                        raise ValueError("❌ El código de barras ya existe en otro producto")
                
                db.cur.execute("""
                    UPDATE productos 
                    SET nombre = %s, descripcion = %s, precio = %s, stock = %s, codigo_barras = %s 
                    WHERE id = %s
                """, (nombre, descripcion, precio, stock, codigo_barras, producto_id))
                
                db.conn.commit()
                messagebox.showinfo("✅ Éxito", "Producto actualizado")
                cargar_productos()
                ventana_actualizar.destroy()
                
            except ValueError as e:
                messagebox.showerror("❌ Error de validación", str(e))
            except Exception as e:
                db.conn.rollback()
                messagebox.showerror("❌ Error", f"No se pudo actualizar: {e}")
        
        # Frame para botones
        btn_frame = tk.Frame(ventana_actualizar, bg=CyberColors.FONDO_PRINCIPAL)
        btn_frame.pack(pady=20)
        
        # Botón guardar
        btn_guardar = crear_boton_estilizado(
            btn_frame,
            "💾 GUARDAR CAMBIOS",
            guardar_cambios,
            CyberColors.BOTON_ACTUALIZAR,
            ancho=20
        )
        btn_guardar.pack(side="left", padx=10)
        
        # Botón cancelar
        btn_cancelar = crear_boton_estilizado(
            btn_frame,
            "❌ CANCELAR",
            ventana_actualizar.destroy,
            CyberColors.BOTON_ELIMINAR,
            ancho=15
        )
        btn_cancelar.pack(side="left", padx=10)
        
    except Exception as e:
        messagebox.showerror("❌ Error", f"Error al abrir actualización: {e}")

# ============================================
# FUNCIONES DE COMPRA Y VENTA
# ============================================
def comprar_producto():
    """Abre ventana para registrar compra"""
    
    def procesar_compra():
        """Procesa la compra en BD"""
        try:
            producto_id = validar_numero(entry_producto_id.get(), 'int', 'ID')
            cantidad = validar_numero(entry_cantidad.get(), 'int', 'cantidad')
            proveedor = validar_texto_no_vacio(entry_proveedor.get(), "Proveedor")
            fecha = datetime.now().strftime('%Y-%m-%d')
            
            if cantidad <= 0:
                raise ValueError("La cantidad debe ser mayor a 0")
            
            # Obtiene datos del producto
            db.cur.execute("SELECT stock, precio FROM productos WHERE id = %s", (producto_id,))
            producto = db.cur.fetchone()
            
            if not producto:
                raise ValueError("Producto no encontrado")
            
            # Calcula nuevo stock y total
            nuevo_stock = producto[0] + cantidad
            total_compra = cantidad * producto[1]
            
            # Verifica si existe la tabla compras
            try:
                # Actualiza stock y registra compra
                db.cur.execute("UPDATE productos SET stock = %s WHERE id = %s", (nuevo_stock, producto_id))
                db.cur.execute("""
                    INSERT INTO compras (producto_id, cantidad, proveedor, fecha, total) 
                    VALUES (%s, %s, %s, %s, %s)
                """, (producto_id, cantidad, proveedor, fecha, total_compra))
            except psycopg2.errors.UndefinedTable:
                # Crear tabla compras si no existe
                db.cur.execute("""
                    CREATE TABLE IF NOT EXISTS compras (
                        id SERIAL PRIMARY KEY,
                        producto_id INTEGER REFERENCES productos(id),
                        cantidad INTEGER NOT NULL,
                        proveedor VARCHAR(100),
                        fecha DATE NOT NULL,
                        total DECIMAL(10,2)
                    )
                """)
                db.cur.execute("UPDATE productos SET stock = %s WHERE id = %s", (nuevo_stock, producto_id))
                db.cur.execute("""
                    INSERT INTO compras (producto_id, cantidad, proveedor, fecha, total) 
                    VALUES (%s, %s, %s, %s, %s)
                """, (producto_id, cantidad, proveedor, fecha, total_compra))
            
            db.conn.commit()
            messagebox.showinfo(
                "✅ COMPRA EXITOSA",
                f"📦 {cantidad} unidades compradas\n💰 Total: ${total_compra:.2f}\n🏢 Proveedor: {proveedor}"
            )
            ventana_compra.destroy()
            cargar_productos()
            
        except ValueError as e:
            messagebox.showerror("❌ Error de validación", str(e))
        except Exception as e:
            db.conn.rollback()
            messagebox.showerror("❌ Error", f"Compra fallida: {e}")

    # Ventana de compra
    ventana_compra = tk.Toplevel(ventana)
    ventana_compra.title("📥 COMPRAR PRODUCTO - CYBER INVENTORY")
    ventana_compra.geometry("400x450")
    ventana_compra.resizable(False, False)
    ventana_compra.configure(bg=CyberColors.FONDO_PRINCIPAL)
    ventana_compra.transient(ventana)
    ventana_compra.grab_set()
    
    centrar_ventana(ventana_compra, 400, 450)
    
    # Título
    titulo = tk.Label(
        ventana_compra,
        text="📥 REGISTRAR COMPRA",
        font=("Segoe UI", 16, "bold"),
        bg=CyberColors.FONDO_PRINCIPAL,
        fg=CyberColors.TEXTO_DORADO
    )
    titulo.pack(pady=20)
    
    # Frame formulario
    form_frame = tk.Frame(ventana_compra, bg=CyberColors.FONDO_SECUNDARIO, padx=30, pady=20)
    form_frame.pack(fill="both", padx=30, pady=10)
    
    # Campos
    labels = ["ID Producto:", "Cantidad:", "Proveedor:"]
    entries = []
    
    for label_text in labels:
        tk.Label(
            form_frame,
            text=label_text,
            font=("Segoe UI", 10),
            bg=CyberColors.FONDO_SECUNDARIO,
            fg=CyberColors.TEXTO_AZUL
        ).pack(pady=(10, 0))
        
        entry = tk.Entry(
            form_frame,
            font=("Segoe UI", 10),
            width=35,
            bg=CyberColors.FONDO_DESTACADO,
            fg=CyberColors.TEXTO_PRINCIPAL,
            insertbackground=CyberColors.TEXTO_DORADO,
            relief="flat",
            bd=2
        )
        entry.pack(pady=5)
        entries.append(entry)
    
    entry_producto_id, entry_cantidad, entry_proveedor = entries
    
    # Frame botones
    btn_frame = tk.Frame(ventana_compra, bg=CyberColors.FONDO_PRINCIPAL)
    btn_frame.pack(pady=20)
    
    # Botón procesar
    btn_procesar = crear_boton_estilizado(
        btn_frame,
        "✅ PROCESAR COMPRA",
        procesar_compra,
        CyberColors.BOTON_COMPRAR,
        ancho=18
    )
    btn_procesar.pack(side="left", padx=10)
    
    # Botón cancelar
    btn_cancelar = crear_boton_estilizado(
        btn_frame,
        "❌ CANCELAR",
        ventana_compra.destroy,
        CyberColors.BOTON_ELIMINAR,
        ancho=15
    )
    btn_cancelar.pack(side="left", padx=10)

def vender_producto():
    """Abre ventana para registrar venta"""
    
    def procesar_venta():
        """Procesa la venta en BD"""
        try:
            producto_id = validar_numero(entry_producto_id.get(), 'int', 'ID')
            cantidad = validar_numero(entry_cantidad.get(), 'int', 'cantidad')
            cliente = validar_texto_no_vacio(entry_cliente.get(), "Cliente")
            fecha = datetime.now().strftime('%Y-%m-%d')
            
            if cantidad <= 0:
                raise ValueError("La cantidad debe ser mayor a 0")
            
            # Verifica stock
            db.cur.execute("SELECT stock, precio FROM productos WHERE id = %s", (producto_id,))
            producto = db.cur.fetchone()
            
            if not producto:
                raise ValueError("Producto no encontrado")
            
            if producto[0] < cantidad:
                raise ValueError(f"Stock insuficiente. Disponible: {producto[0]}")
            
            # Calcula nuevo stock y total
            nuevo_stock = producto[0] - cantidad
            total_venta = cantidad * producto[1]
            
            # Verifica si existe la tabla ventas
            try:
                # Actualiza stock y registra venta
                db.cur.execute("UPDATE productos SET stock = %s WHERE id = %s", (nuevo_stock, producto_id))
                db.cur.execute("""
                    INSERT INTO ventas (producto_id, cantidad, cliente, fecha, total) 
                    VALUES (%s, %s, %s, %s, %s)
                """, (producto_id, cantidad, cliente, fecha, total_venta))
            except psycopg2.errors.UndefinedTable:
                # Crear tabla ventas si no existe
                db.cur.execute("""
                    CREATE TABLE IF NOT EXISTS ventas (
                        id SERIAL PRIMARY KEY,
                        producto_id INTEGER REFERENCES productos(id),
                        cantidad INTEGER NOT NULL,
                        cliente VARCHAR(100),
                        fecha DATE NOT NULL,
                        total DECIMAL(10,2)
                    )
                """)
                db.cur.execute("UPDATE productos SET stock = %s WHERE id = %s", (nuevo_stock, producto_id))
                db.cur.execute("""
                    INSERT INTO ventas (producto_id, cantidad, cliente, fecha, total) 
                    VALUES (%s, %s, %s, %s, %s)
                """, (producto_id, cantidad, cliente, fecha, total_venta))
            
            db.conn.commit()
            messagebox.showinfo(
                "✅ VENTA EXITOSA",
                f"💰 Total: ${total_venta:.2f}\n👤 Cliente: {cliente}"
            )
            ventana_venta.destroy()
            cargar_productos()
            
        except ValueError as e:
            messagebox.showerror("❌ Error de validación", str(e))
        except Exception as e:
            db.conn.rollback()
            messagebox.showerror("❌ Error", f"Venta fallida: {e}")

    # Ventana de venta
    ventana_venta = tk.Toplevel(ventana)
    ventana_venta.title("📤 VENDER PRODUCTO - CYBER INVENTORY")
    ventana_venta.geometry("400x450")
    ventana_venta.resizable(False, False)
    ventana_venta.configure(bg=CyberColors.FONDO_PRINCIPAL)
    ventana_venta.transient(ventana)
    ventana_venta.grab_set()
    
    centrar_ventana(ventana_venta, 400, 450)
    
    # Título
    titulo = tk.Label(
        ventana_venta,
        text="📤 REGISTRAR VENTA",
        font=("Segoe UI", 16, "bold"),
        bg=CyberColors.FONDO_PRINCIPAL,
        fg=CyberColors.TEXTO_DORADO
    )
    titulo.pack(pady=20)
    
    # Frame formulario
    form_frame = tk.Frame(ventana_venta, bg=CyberColors.FONDO_SECUNDARIO, padx=30, pady=20)
    form_frame.pack(fill="both", padx=30, pady=10)
    
    # Campos
    labels = ["ID Producto:", "Cantidad:", "Cliente:"]
    entries = []
    
    for label_text in labels:
        tk.Label(
            form_frame,
            text=label_text,
            font=("Segoe UI", 10),
            bg=CyberColors.FONDO_SECUNDARIO,
            fg=CyberColors.TEXTO_AZUL
        ).pack(pady=(10, 0))
        
        entry = tk.Entry(
            form_frame,
            font=("Segoe UI", 10),
            width=35,
            bg=CyberColors.FONDO_DESTACADO,
            fg=CyberColors.TEXTO_PRINCIPAL,
            insertbackground=CyberColors.TEXTO_DORADO,
            relief="flat",
            bd=2
        )
        entry.pack(pady=5)
        entries.append(entry)
    
    entry_producto_id, entry_cantidad, entry_cliente = entries
    
    # Frame botones
    btn_frame = tk.Frame(ventana_venta, bg=CyberColors.FONDO_PRINCIPAL)
    btn_frame.pack(pady=20)
    
    # Botón procesar
    btn_procesar = crear_boton_estilizado(
        btn_frame,
        "💰 PROCESAR VENTA",
        procesar_venta,
        CyberColors.BOTON_VENDER,
        ancho=18
    )
    btn_procesar.pack(side="left", padx=10)
    
    # Botón cancelar
    btn_cancelar = crear_boton_estilizado(
        btn_frame,
        "❌ CANCELAR",
        ventana_venta.destroy,
        CyberColors.BOTON_ELIMINAR,
        ancho=15
    )
    btn_cancelar.pack(side="left", padx=10)

def actualizar_contador():
    """Actualiza el contador de registros"""
    try:
        db.cur.execute("SELECT COUNT(*) FROM productos")
        total = db.cur.fetchone()[0]
        lbl_contador.config(text=f"📊 TOTAL REGISTROS: {total} | CYBER INVENTORY 2026")
    except:
        lbl_contador.config(text="📊 TOTAL REGISTROS: ERROR")

def mostrar_balance():
    """Muestra balance financiero"""
    try:
        # Verificar si las tablas existen
        try:
            db.cur.execute("SELECT COALESCE(SUM(total), 0) FROM ventas")
            ventas = db.cur.fetchone()[0]
        except:
            ventas = 0
        
        db.cur.execute("SELECT COALESCE(SUM(precio * stock), 0) FROM productos")
        inventario = db.cur.fetchone()[0]
        
        # Mensaje con estilo
        mensaje = f"""
        ═══════════════════════════════════
              📊 BALANCE GENERAL
        ═══════════════════════════════════
        
        💰 TOTAL VENTAS:    ${ventas:,.2f}
        📦 VALOR INVENTARIO: ${inventario:,.2f}
        
        ═══════════════════════════════════
        💵 TOTAL ACTIVOS:   ${ventas + inventario:,.2f}
        ═══════════════════════════════════
        """
        
        messagebox.showinfo("💰 BALANCE GENERAL - CYBER INVENTORY", mensaje)
        
    except Exception as e:
        messagebox.showerror("❌ Error", f"No se pudo obtener el balance: {e}")

# ============================================
# CONFIGURACIÓN DE INTERFAZ PRINCIPAL
# ============================================
# Ventana principal
ventana = tk.Tk()
ventana.title("🏢 CYBER INVENTORY 2026 - SISTEMA DE GESTIÓN")
ventana.geometry("1300x650")
ventana.minsize(1200, 600)
ventana.configure(bg=CyberColors.FONDO_PRINCIPAL)

# Configuración de estilos para ttk
style = ttk.Style()
style.theme_use('clam')

# Personalizar TreeView
style.configure(
    "Treeview",
    background=CyberColors.FONDO_SECUNDARIO,
    foreground=CyberColors.TEXTO_PRINCIPAL,
    fieldbackground=CyberColors.FONDO_SECUNDARIO,
    font=("Segoe UI", 9)
)

style.configure(
    "Treeview.Heading",
    background=CyberColors.FONDO_DESTACADO,
    foreground=CyberColors.TEXTO_DORADO,
    font=("Segoe UI", 10, "bold"),
    relief="flat"
)

style.map(
    "Treeview",
    background=[('selected', CyberColors.AZUL_NEON + '33')],
    foreground=[('selected', CyberColors.TEXTO_PRINCIPAL)]
)

# ============================================
# INICIALIZACIÓN BD
# ============================================
db = ConexionDB()
if not db.cur:
    messagebox.showerror(
        "❌ ERROR CRÍTICO",
        "No se pudo conectar a la base de datos.\nVerifique la conexión."
    )
    ventana.quit()

# ============================================
# CONSTRUCCIÓN INTERFAZ
# ============================================
# Frame principal con padding
main_frame = tk.Frame(ventana, bg=CyberColors.FONDO_PRINCIPAL)
main_frame.pack(fill="both", expand=True, padx=15, pady=15)

# ----- ENCABEZADO -----
header_frame = tk.Frame(main_frame, bg=CyberColors.FONDO_DESTACADO, height=60)
header_frame.pack(fill="x", pady=(0, 15))
header_frame.pack_propagate(False)

# Título del sistema
titulo_sistema = tk.Label(
    header_frame,
    text="⚡ CYBER INVENTORY 2026 ⚡",
    font=("Segoe UI", 20, "bold"),
    bg=CyberColors.FONDO_DESTACADO,
    fg=CyberColors.TEXTO_DORADO
)
titulo_sistema.pack(side="left", padx=20, pady=10)

# Versión
version_label = tk.Label(
    header_frame,
    text="v8.0 CYBER EDITION",
    font=("Segoe UI", 10),
    bg=CyberColors.FONDO_DESTACADO,
    fg=CyberColors.TEXTO_AZUL
)
version_label.pack(side="right", padx=20, pady=10)

# ----- FRAME DE BÚSQUEDA -----
search_frame = tk.Frame(main_frame, bg=CyberColors.FONDO_PRINCIPAL)
search_frame.pack(fill="x", pady=5)

# Label búsqueda
lbl_buscar = tk.Label(
    search_frame,
    text="🔍 BUSCAR PRODUCTO:",
    font=("Segoe UI", 10, "bold"),
    bg=CyberColors.FONDO_PRINCIPAL,
    fg=CyberColors.TEXTO_AZUL
)
lbl_buscar.pack(side="left", padx=5)

# Campo de búsqueda
entry_buscar = tk.Entry(
    search_frame,
    font=("Segoe UI", 10),
    width=50,
    bg=CyberColors.FONDO_SECUNDARIO,
    fg=CyberColors.TEXTO_PRINCIPAL,
    insertbackground=CyberColors.TEXTO_DORADO,
    relief="flat",
    bd=2
)
entry_buscar.pack(side="left", padx=5)
entry_buscar.bind("<KeyRelease>", buscar_producto)

# Botón limpiar
btn_limpiar = crear_boton_estilizado(
    search_frame,
    "🗑️ LIMPIAR",
    lambda: [entry_buscar.delete(0, tk.END), cargar_productos()],
    CyberColors.FONDO_DESTACADO,
    ancho=12
)
btn_limpiar.pack(side="left", padx=5)

# ----- TREEWVIEW (TABLA) -----
tree_frame = tk.Frame(main_frame, bg=CyberColors.FONDO_SECUNDARIO)
tree_frame.pack(fill="both", expand=True, pady=10)

# Scrollbars
scrollbar_y = ttk.Scrollbar(tree_frame)
scrollbar_y.pack(side="right", fill="y")

scrollbar_x = ttk.Scrollbar(tree_frame, orient="horizontal")
scrollbar_x.pack(side="bottom", fill="x")

# Treeview
treeview_productos = ttk.Treeview(
    tree_frame,
    columns=("id", "nombre", "descripcion", "precio", "stock", "codigo_barras"),
    show="headings",
    yscrollcommand=scrollbar_y.set,
    xscrollcommand=scrollbar_x.set,
    height=15
)

# Configuración de columnas
columnas = [
    ("id", "ID", 50, "center"),
    ("nombre", "NOMBRE", 200, "w"),
    ("descripcion", "DESCRIPCIÓN", 350, "w"),
    ("precio", "PRECIO", 120, "e"),
    ("stock", "STOCK", 100, "center"),
    ("codigo_barras", "CÓDIGO BARRAS", 150, "center")
]

for col, heading, width, anchor in columnas:
    treeview_productos.column(col, width=width, anchor=anchor)
    treeview_productos.heading(col, text=heading)

treeview_productos.pack(fill="both", expand=True)

# Configurar scrollbars
scrollbar_y.config(command=treeview_productos.yview)
scrollbar_x.config(command=treeview_productos.xview)

# ----- FRAME DE BOTONES DE ACCIÓN -----
button_frame = tk.Frame(main_frame, bg=CyberColors.FONDO_PRINCIPAL)
button_frame.pack(fill="x", pady=15)

# Configuración de botones en grid
botones_config = [
    # Fila 0
    ("➕ AGREGAR", agregar_producto, CyberColors.BOTON_AGREGAR),
    ("✏️ EDITAR", actualizar_producto, CyberColors.BOTON_EDITAR),
    ("❌ ELIMINAR", eliminar_producto, CyberColors.BOTON_ELIMINAR),
    # Fila 1
    ("📥 COMPRAR", comprar_producto, CyberColors.BOTON_COMPRAR),
    ("📤 VENDER", vender_producto, CyberColors.BOTON_VENDER),
    ("📊 BALANCE", mostrar_balance, CyberColors.BOTON_BALANCE),
    ("🔄 ACTUALIZAR", lambda: cargar_productos(), CyberColors.BOTON_ACTUALIZAR)
]

# Crear botones en grid
for i, (texto, comando, color) in enumerate(botones_config):
    fila = 0 if i < 3 else 1
    columna = i if i < 3 else i - 3
    
    btn = crear_boton_estilizado(
        button_frame,
        texto,
        comando,
        color,
        ancho=14
    )
    btn.grid(row=fila, column=columna, padx=5, pady=5)

# ----- BARRA DE ESTADO -----
status_frame = tk.Frame(main_frame, bg=CyberColors.FONDO_DESTACADO, height=35)
status_frame.pack(fill="x", pady=(10, 0))
status_frame.pack_propagate(False)

# Contador de registros
lbl_contador = tk.Label(
    status_frame,
    text="📊 TOTAL REGISTROS: CARGANDO... | CYBER INVENTORY 2026",
    font=("Segoe UI", 9),
    bg=CyberColors.FONDO_DESTACADO,
    fg=CyberColors.TEXTO_AZUL
)
lbl_contador.pack(side="left", padx=10, pady=5)

# Estado de conexión
lbl_conexion = tk.Label(
    status_frame,
    text="✅ CONECTADO A POSTGRESQL",
    font=("Segoe UI", 9, "bold"),
    bg=CyberColors.FONDO_DESTACADO,
    fg=CyberColors.TEXTO_DORADO
)
lbl_conexion.pack(side="right", padx=10, pady=5)

# ============================================
# CARGA INICIAL
# ============================================
cargar_productos()

# ============================================
# MANEJO DE CIERRE
# ============================================
def on_closing():
    """Maneja el cierre de la aplicación"""
    if messagebox.askokcancel(
        "👋 SALIR",
        "¿Cerrar CYBER INVENTORY 2026?"
    ):
        if db:
            db.close()
        ventana.destroy()

ventana.protocol("WM_DELETE_WINDOW", on_closing)

# ============================================
# INICIO DE APLICACIÓN
# ============================================
if __name__ == "__main__":
    ventana.mainloop()