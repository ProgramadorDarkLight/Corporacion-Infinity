import psycopg2
from psycopg2 import OperationalError
import sys

print("=" * 70)
print("DIAGNÓSTICO DE CONEXIÓN POSTGRESQL")
print("=" * 70)

# 1. Verificar versión de psycopg2
print(f"\n📦 Versión de psycopg2: {psycopg2.__version__}")
print(f"🐍 Versión de Python: {sys.version}")

# 2. Probar diferentes configuraciones
configuraciones = [
    {
        "nombre": "DarkLight localhost con contraseña",
        "params": {
            "dbname": "hormiguero_db",
            "user": "DarkLight",
            "password": "Zeus9119*",
            "host": "localhost",
            "port": "5432",
            "connect_timeout": 5
        }
    },
    {
        "nombre": "DarkLight 127.0.0.1 con contraseña",
        "params": {
            "dbname": "hormiguero_db",
            "user": "DarkLight",
            "password": "Zeus9119*",
            "host": "127.0.0.1",
            "port": "5432",
            "connect_timeout": 5
        }
    },
    {
        "nombre": "DarkLight sin contraseña",
        "params": {
            "dbname": "hormiguero_db",
            "user": "DarkLight",
            "host": "localhost",
            "port": "5432",
            "connect_timeout": 5
        }
    },
    {
        "nombre": "postgres con contraseña",
        "params": {
            "dbname": "hormiguero_db",
            "user": "postgres",
            "password": "admin123",  # Cambia si es diferente
            "host": "localhost",
            "port": "5432",
            "connect_timeout": 5
        }
    }
]

conexion_exitosa = False

for config in configuraciones:
    print(f"\n▶ Probando: {config['nombre']}")
    try:
        conn = psycopg2.connect(**config['params'])
        cur = conn.cursor()
        
        # Probar conexión
        cur.execute("SELECT version();")
        version = cur.fetchone()
        print(f"  ✅ ¡CONEXIÓN EXITOSA!")
        print(f"  PostgreSQL: {version[0][:50]}...")
        
        # Verificar tablas
        cur.execute("SELECT COUNT(*) FROM usuarios;")
        count = cur.fetchone()
        print(f"  Usuarios en DB: {count[0]}")
        
        cur.execute("SELECT username, tipo_usuario FROM usuarios LIMIT 3;")
        for row in cur.fetchall():
            print(f"  - {row[0]} ({row[1]})")
        
        conn.close()
        print("  ✅ Conexión cerrada correctamente")
        conexion_exitosa = True
        break
        
    except OperationalError as e:
        print(f"  ❌ Error de operación: {str(e)[:100]}")
        if "password" in str(e).lower():
            print("     → Contraseña incorrecta o método de autenticación no soportado")
        elif "does not exist" in str(e).lower():
            print("     → La base de datos no existe")
        elif "connection refused" in str(e).lower():
            print("     → PostgreSQL no está corriendo en ese puerto")
        elif "SCRAM" in str(e):
            print("     → Error de autenticación SCRAM")
            
    except Exception as e:
        print(f"  ❌ Error inesperado: {type(e).__name__}: {e}")

if not conexion_exitosa:
    print("\n" + "=" * 70)
    print("🔴 NINGUNA CONEXIÓN FUNCIONÓ")
    print("=" * 70)
    print("\nPOSIBLES SOLUCIONES:")
    print("1. Verifica que PostgreSQL esté corriendo")
    print("2. Cambia la contraseña: ALTER USER DarkLight WITH PASSWORD 'Zeus9119*';")
    print("3. Configura pg_hba.conf para aceptar conexiones")
    print("4. Usa el usuario 'postgres' en tu código")
else:
    print("\n" + "=" * 70)
    print("🟢 CONEXIÓN EXITOSA")
    print("=" * 70)