import hashlib
import psycopg2

def cambiar_contraseña():
    print("=" * 50)
    print("🔑 CAMBIAR CONTRASEÑA DE USUARIO")
    print("=" * 50)
    
    # Conectar a la base de datos
    try:
        conn = psycopg2.connect(
            dbname="hormiguero_db",
            user="DarkLight",
            password="Zeus9119*",
            host="localhost",
            port="5432"
        )
        cur = conn.cursor()
        print("✅ Conectado a la base de datos\n")
        
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return
    
    # Mostrar usuarios existentes
    cur.execute("SELECT id, username, tipo_usuario FROM usuarios ORDER BY id;")
    usuarios = cur.fetchall()
    
    print("📋 USUARIOS EXISTENTES:")
    print("-" * 40)
    for user in usuarios:
        print(f"  ID: {user[0]} | Usuario: {user[1]} | Tipo: {user[2]}")
    print("-" * 40)
    
    # Solicitar datos
    usuario = input("\n👤 Ingresa el nombre de usuario a modificar: ").strip()
    nueva_contraseña = input("🔑 Ingresa la nueva contraseña: ").strip()
    
    if not usuario or not nueva_contraseña:
        print("❌ Datos incompletos")
        conn.close()
        return
    
    # Generar hash SHA-256
    hash_password = hashlib.sha256(nueva_contraseña.encode()).hexdigest()
    print(f"\n📝 Hash generado: {hash_password[:20]}...")
    
    # Actualizar en la base de datos
    try:
        cur.execute("""
            UPDATE usuarios 
            SET password = %s 
            WHERE username = %s
        """, (hash_password, usuario))
        
        conn.commit()
        
        if cur.rowcount > 0:
            print(f"\n✅ ¡Contraseña actualizada exitosamente!")
            print(f"   Usuario: {usuario}")
            print(f"   Nueva contraseña: {nueva_contraseña}")
        else:
            print(f"\n❌ Usuario '{usuario}' no encontrado")
            
    except Exception as e:
        print(f"❌ Error al actualizar: {e}")
        conn.rollback()
    
    conn.close()
    print("\n🔌 Conexión cerrada")

if __name__ == "__main__":
    cambiar_contraseña()