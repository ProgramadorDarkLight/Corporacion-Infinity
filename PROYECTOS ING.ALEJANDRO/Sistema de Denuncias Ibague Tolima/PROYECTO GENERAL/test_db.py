import psycopg2
from psycopg2.extras import RealDictCursor

try:
    conn = psycopg2.connect(
        dbname='sistema_app_denuncias',
        user='DarkLight',
        password='Zeus9119',
        host='localhost',
        port='5432'
    )
    print("✅ Conexión exitosa a PostgreSQL")
    
    cur = conn.cursor()
    cur.execute("SELECT * FROM usuarios")
    usuarios = cur.fetchall()
    print(f"✅ Usuarios encontrados: {len(usuarios)}")
    cur.close()
    conn.close()
except Exception as e:
    print(f"❌ Error: {e}")