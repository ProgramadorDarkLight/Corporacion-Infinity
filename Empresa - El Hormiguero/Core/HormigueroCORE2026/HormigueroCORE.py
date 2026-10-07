import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import psycopg2
from datetime import datetime
import hashlib

# Conexión a la base de datos PostgreSQL
class ConexionDB:
    def __init__(self, dbname="hormiguero_db", user="DarkLight", password="Zeus9119*", host="localhost", port="5432"):
        try:
            self.conn = psycopg2.connect(
                dbname=dbname, 
                user=user, 
                password=password, 
                host=host, 
                port=port
            )
            self.cur = self.conn.cursor()
            self.crear_tablas()
            print("Conexión a la base de datos establecida")
        except Exception as e:
            print(f"Error al conectar a la base de datos: {e}")
            self.conn = None
            self.cur = None

    def crear_tablas(self):
        """Crear las tablas necesarias si no existen"""
        try:
            # Tabla de usuarios
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    email VARCHAR(100),
                    tipo_usuario VARCHAR(20) DEFAULT 'ciudadano',
                    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    activo BOOLEAN DEFAULT TRUE
                )
            """)
            
            # Tabla de noticias/denuncias
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS noticias (
                    id SERIAL PRIMARY KEY,
                    titulo VARCHAR(200) NOT NULL,
                    contenido TEXT NOT NULL,
                    categoria VARCHAR(50),
                    ubicacion VARCHAR(200),
                    evidencia_path VARCHAR(500),
                    estado VARCHAR(20) DEFAULT 'pendiente',
                    usuario_id INTEGER REFERENCES usuarios(id),
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_publicacion TIMESTAMP,
                    visitas INTEGER DEFAULT 0,
                    revisado_por INTEGER REFERENCES usuarios(id)
                )
            """)
            
            # Tabla de evidencias multimedia
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS evidencias (
                    id SERIAL PRIMARY KEY,
                    noticia_id INTEGER REFERENCES noticias(id) ON DELETE CASCADE,
                    tipo_evidencia VARCHAR(20),
                    ruta_archivo VARCHAR(500),
                    descripcion TEXT,
                    fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla de comentarios
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS comentarios (
                    id SERIAL PRIMARY KEY,
                    noticia_id INTEGER REFERENCES noticias(id) ON DELETE CASCADE,
                    usuario_id INTEGER REFERENCES usuarios(id),
                    comentario TEXT NOT NULL,
                    fecha_comentario TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insertar usuario administrador por defecto si no existe
            self.cur.execute("SELECT * FROM usuarios WHERE username = 'admin'")
            if not self.cur.fetchone():
                password_hash = hashlib.sha256("admin123".encode()).hexdigest()
                self.cur.execute("""
                    INSERT INTO usuarios (username, password, email, tipo_usuario) 
                    VALUES (%s, %s, %s, %s)
                """, ("admin", password_hash, "admin@hormiguero.com", "revisor"))
            
            self.conn.commit()
            print("Tablas creadas/verificadas exitosamente")
            
        except Exception as e:
            print(f"Error al crear tablas: {e}")
            self.conn.rollback()

    def close(self):
        if self.conn:
            self.conn.close()

# Ventana de Login
class LoginWindow:
    def __init__(self):
        self.ventana = tk.Tk()
        self.ventana.title("El Hormiguero Ibagué - Sistema de Denuncias")
        self.ventana.geometry("400x350") # Un poco más alta por los botones
        
        # Centrar la ventana
        self.ventana.eval('tk::PlaceWindow . center')
        
        # Estilo
        self.ventana.configure(bg='#f0f0f0')
        
        # Título
        titulo = tk.Label(self.ventana, text="El Hormiguero Ibagué", 
                         font=("Arial", 16, "bold"), bg='#f0f0f0', fg='#333')
        titulo.pack(pady=20)
        
        subtitulo = tk.Label(self.ventana, text="Medio de Comunicación Investigativo Alternativo",
                            font=("Arial", 10), bg='#f0f0f0', fg='#666')
        subtitulo.pack(pady=5)
        
        # Frame para login
        frame_login = tk.Frame(self.ventana, bg='#f0f0f0')
        frame_login.pack(pady=10)
        
        # Usuario
        tk.Label(frame_login, text="Usuario:", bg='#f0f0f0', font=("Arial", 10)).grid(row=0, column=0, pady=5, padx=5)
        self.entry_usuario = tk.Entry(frame_login, width=25)
        self.entry_usuario.grid(row=0, column=1, pady=5, padx=5)
        
        # Contraseña
        tk.Label(frame_login, text="Contraseña:", bg='#f0f0f0', font=("Arial", 10)).grid(row=1, column=0, pady=5, padx=5)
        self.entry_password = tk.Entry(frame_login, show="*", width=25)
        self.entry_password.grid(row=1, column=1, pady=5, padx=5)
        
        # Botón login
        btn_login = tk.Button(self.ventana, text="Iniciar Sesión", command=self.login,
                            bg='#4CAF50', fg='white', font=("Arial", 10), width=25)
        btn_login.pack(pady=10)
        
        # Botón registro
        btn_registro = tk.Button(self.ventana, text="Registrarse como Ciudadano", command=self.registro,
                               bg='#2196F3', fg='white', font=("Arial", 10), width=25)
        btn_registro.pack(pady=5)
        
        self.db = ConexionDB()

    def login(self):
        # 1. Obtener y limpiar datos
        username = self.entry_usuario.get().strip()
        password = self.entry_password.get().strip()
        
        if not username or not password:
            messagebox.showwarning("Atención", "Por favor, ingrese usuario y contraseña")
            return

        # 2. Generar hash
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        print(f"--- Intento de Login: {username} ---")

        try:
            # 3. Consulta a la base de datos
            self.db.cur.execute("""
                SELECT id, username, tipo_usuario 
                FROM usuarios 
                WHERE username = %s AND password = %s AND activo = TRUE
            """, (username, password_hash))
            
            usuario = self.db.cur.fetchone()
            
            if usuario:
                print(f"Acceso concedido: {usuario[1]} ({usuario[2]})")
                self.ventana.destroy() 
                
                if usuario[2] == 'revisor':
                    RevisorWindow(usuario[0], usuario[1])
                else:
                    CiudadanoWindow(usuario[0], usuario[1])
            else:
                print("Acceso denegado: Credenciales incorrectas.")
                messagebox.showerror("Error", "Usuario o contraseña incorrectos")
                
        except Exception as e:
            print(f"Error en login: {e}")
            messagebox.showerror("Error", f"Error al conectar con la base de datos: {e}")

    def registro(self):
        RegistroWindow(self.db)
    
    def run(self):
        self.ventana.mainloop()

# Ventana de Registro
class RegistroWindow:
    def __init__(self, db):
        self.db = db
        self.ventana = tk.Toplevel()
        self.ventana.title("Registro de Ciudadano")
        self.ventana.geometry("400x350")
        
        # Centrar ventana
        self.ventana.eval('tk::PlaceWindow . center')
        
        # Campos
        tk.Label(self.ventana, text="Registro de Usuario", font=("Arial", 14, "bold")).pack(pady=10)
        
        frame = tk.Frame(self.ventana)
        frame.pack(pady=20)
        
        tk.Label(frame, text="Usuario:").grid(row=0, column=0, pady=5, padx=5, sticky='e')
        self.entry_usuario = tk.Entry(frame, width=30)
        self.entry_usuario.grid(row=0, column=1, pady=5, padx=5)
        
        tk.Label(frame, text="Correo:").grid(row=1, column=0, pady=5, padx=5, sticky='e')
        self.entry_email = tk.Entry(frame, width=30)
        self.entry_email.grid(row=1, column=1, pady=5, padx=5)
        
        tk.Label(frame, text="Contraseña:").grid(row=2, column=0, pady=5, padx=5, sticky='e')
        self.entry_password = tk.Entry(frame, show="*", width=30)
        self.entry_password.grid(row=2, column=1, pady=5, padx=5)
        
        tk.Label(frame, text="Confirmar:").grid(row=3, column=0, pady=5, padx=5, sticky='e')
        self.entry_confirm = tk.Entry(frame, show="*", width=30)
        self.entry_confirm.grid(row=3, column=1, pady=5, padx=5)
        
        btn_registrar = tk.Button(self.ventana, text="Registrar", command=self.registrar,
                                 bg='#4CAF50', fg='white')
        btn_registrar.pack(pady=10)
        
    def registrar(self):
        usuario = self.entry_usuario.get()
        email = self.entry_email.get()
        password = self.entry_password.get()
        confirm = self.entry_confirm.get()
        
        if not usuario or not email or not password:
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return
            
        if password != confirm:
            messagebox.showerror("Error", "Las contraseñas no coinciden")
            return
            
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        try:
            self.db.cur.execute("""
                INSERT INTO usuarios (username, password, email, tipo_usuario)
                VALUES (%s, %s, %s, 'ciudadano')
            """, (usuario, password_hash, email))
            self.db.conn.commit()
            
            messagebox.showinfo("Éxito", "Usuario registrado exitosamente")
            self.ventana.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar: {e}")

# Ventana para Ciudadanos (Denunciantes)
class CiudadanoWindow:
    def __init__(self, usuario_id, username):
        self.usuario_id = usuario_id
        self.username = username
        self.ventana = tk.Tk()
        self.ventana.title(f"El Hormiguero Ibagué - Bienvenido {username}")
        self.ventana.geometry("800x600")
        
        self.db = ConexionDB()
        self.crear_interfaz()
        self.cargar_mis_noticias()
        
    def crear_interfaz(self):
        # Menú superior
        menu = tk.Menu(self.ventana)
        self.ventana.config(menu=menu)
        
        menu_archivo = tk.Menu(menu)
        menu.add_cascade(label="Archivo", menu=menu_archivo)
        menu_archivo.add_command(label="Cerrar Sesión", command=self.cerrar_sesion)
        menu_archivo.add_command(label="Salir", command=self.ventana.quit)
        
        # Frame principal con tabs
        self.notebook = ttk.Notebook(self.ventana)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab para crear denuncia
        self.tab_crear = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_crear, text="Nueva Denuncia")
        self.crear_formulario_denuncia()
        
        # Tab para mis denuncias
        self.tab_mis = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_mis, text="Mis Denuncias")
        self.crear_lista_denuncias()
        
    def crear_formulario_denuncia(self):
        # Título
        tk.Label(self.tab_crear, text="Formulario de Denuncia", 
                font=("Arial", 14, "bold")).pack(pady=10)
        
        # Frame para el formulario
        frame = tk.Frame(self.tab_crear)
        frame.pack(pady=10, padx=20)
        
        # Título
        tk.Label(frame, text="Título:").grid(row=0, column=0, pady=5, padx=5, sticky='e')
        self.entry_titulo = tk.Entry(frame, width=50)
        self.entry_titulo.grid(row=0, column=1, pady=5, padx=5)
        
        # Categoría
        tk.Label(frame, text="Categoría:").grid(row=1, column=0, pady=5, padx=5, sticky='e')
        self.combo_categoria = ttk.Combobox(frame, values=["Corrupción", "Inseguridad", "Servicios Públicos", 
                                                           "Medio Ambiente", "Derechos Humanos", "Otros"])
        self.combo_categoria.grid(row=1, column=1, pady=5, padx=5, sticky='w')
        
        # Ubicación
        tk.Label(frame, text="Ubicación:").grid(row=2, column=0, pady=5, padx=5, sticky='e')
        self.entry_ubicacion = tk.Entry(frame, width=50)
        self.entry_ubicacion.grid(row=2, column=1, pady=5, padx=5)
        
        # Contenido
        tk.Label(frame, text="Contenido:").grid(row=3, column=0, pady=5, padx=5, sticky='ne')
        self.text_contenido = scrolledtext.ScrolledText(frame, width=50, height=10)
        self.text_contenido.grid(row=3, column=1, pady=5, padx=5)
        
        # Evidencia (simulada)
        tk.Label(frame, text="Evidencia:").grid(row=4, column=0, pady=5, padx=5, sticky='e')
        self.entry_evidencia = tk.Entry(frame, width=40)
        self.entry_evidencia.grid(row=4, column=1, pady=5, padx=5, sticky='w')
        btn_evidencia = tk.Button(frame, text="Seleccionar Archivo", command=self.seleccionar_archivo)
        btn_evidencia.grid(row=4, column=2, pady=5, padx=5)
        
        # Botón enviar
        btn_enviar = tk.Button(self.tab_crear, text="Enviar Denuncia", command=self.enviar_denuncia,
                              bg='#4CAF50', fg='white', font=("Arial", 12))
        btn_enviar.pack(pady=20)
        
    def seleccionar_archivo(self):
        from tkinter import filedialog
        archivo = filedialog.askopenfilename(title="Seleccionar evidencia", 
                                            filetypes=[("Imágenes", "*.jpg *.png *.jpeg"), 
                                                      ("Documentos", "*.pdf *.docx"), 
                                                      ("Todos los archivos", "*.*")])
        if archivo:
            self.entry_evidencia.delete(0, tk.END)
            self.entry_evidencia.insert(0, archivo)
    
    def enviar_denuncia(self):
        titulo = self.entry_titulo.get()
        contenido = self.text_contenido.get("1.0", tk.END).strip()
        categoria = self.combo_categoria.get()
        ubicacion = self.entry_ubicacion.get()
        evidencia = self.entry_evidencia.get()
        
        if not titulo or not contenido:
            messagebox.showerror("Error", "Título y contenido son obligatorios")
            return
        
        try:
            self.db.cur.execute("""
                INSERT INTO noticias (titulo, contenido, categoria, ubicacion, evidencia_path, 
                                    estado, usuario_id)
                VALUES (%s, %s, %s, %s, %s, 'pendiente', %s)
            """, (titulo, contenido, categoria, ubicacion, evidencia, self.usuario_id))
            self.db.conn.commit()
            
            messagebox.showinfo("Éxito", "Denuncia enviada correctamente")
            
            # Limpiar formulario
            self.entry_titulo.delete(0, tk.END)
            self.text_contenido.delete("1.0", tk.END)
            self.combo_categoria.set('')
            self.entry_ubicacion.delete(0, tk.END)
            self.entry_evidencia.delete(0, tk.END)
            
            # Recargar mis denuncias
            self.cargar_mis_noticias()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo enviar la denuncia: {e}")
    
    def crear_lista_denuncias(self):
        # Treeview para mostrar mis denuncias
        self.tree_mis = ttk.Treeview(self.tab_mis, columns=("id", "titulo", "categoria", "estado", "fecha"), 
                                     show="headings")
        self.tree_mis.heading("id", text="ID")
        self.tree_mis.heading("titulo", text="Título")
        self.tree_mis.heading("categoria", text="Categoría")
        self.tree_mis.heading("estado", text="Estado")
        self.tree_mis.heading("fecha", text="Fecha")
        
        self.tree_mis.column("id", width=50)
        self.tree_mis.column("titulo", width=200)
        self.tree_mis.column("categoria", width=100)
        self.tree_mis.column("estado", width=100)
        self.tree_mis.column("fecha", width=150)
        
        self.tree_mis.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Botón para ver detalles
        btn_ver = tk.Button(self.tab_mis, text="Ver Detalles", command=self.ver_detalles)
        btn_ver.pack(pady=5)
    
    def cargar_mis_noticias(self):
        # Limpiar treeview
        for item in self.tree_mis.get_children():
            self.tree_mis.delete(item)
        
        try:
            self.db.cur.execute("""
                SELECT id, titulo, categoria, estado, 
                       TO_CHAR(fecha_creacion, 'DD/MM/YYYY HH24:MI') as fecha
                FROM noticias 
                WHERE usuario_id = %s
                ORDER BY fecha_creacion DESC
            """, (self.usuario_id,))
            
            for noticia in self.db.cur.fetchall():
                self.tree_mis.insert("", "end", values=noticia)
                
        except Exception as e:
            print(f"Error al cargar noticias: {e}")
    
    def ver_detalles(self):
        seleccion = self.tree_mis.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione una denuncia")
            return
        
        item = self.tree_mis.item(seleccion[0])
        noticia_id = item['values'][0]
        
        DetallesNoticiaWindow(self.db, noticia_id, self.usuario_id)
    
    def cerrar_sesion(self):
        self.ventana.destroy()
        LoginWindow().run()

# Ventana para Revisores (Editores)
class RevisorWindow:
    def __init__(self, usuario_id, username):
        self.usuario_id = usuario_id
        self.username = username
        self.ventana = tk.Tk()
        self.ventana.title(f"El Hormiguero Ibagué - Panel de Revisor - {username}")
        self.ventana.geometry("1000x700")
        
        self.db = ConexionDB()
        self.crear_interfaz()
        self.cargar_noticias_pendientes()
        
    def crear_interfaz(self):
        # Menú superior
        menu = tk.Menu(self.ventana)
        self.ventana.config(menu=menu)
        
        menu_archivo = tk.Menu(menu)
        menu.add_cascade(label="Archivo", menu=menu_archivo)
        menu_archivo.add_command(label="Cerrar Sesión", command=self.cerrar_sesion)
        menu_archivo.add_command(label="Salir", command=self.ventana.quit)
        
        # Frame principal con tabs
        self.notebook = ttk.Notebook(self.ventana)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab para noticias pendientes
        self.tab_pendientes = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_pendientes, text="Pendientes de Revisión")
        self.crear_lista_pendientes()
        
        # Tab para noticias publicadas
        self.tab_publicadas = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_publicadas, text="Publicadas")
        self.crear_lista_publicadas()
        
        # Tab para estadísticas
        self.tab_estadisticas = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_estadisticas, text="Estadísticas")
        self.mostrar_estadisticas()
    
    def crear_lista_pendientes(self):
        # Treeview para noticias pendientes
        self.tree_pendientes = ttk.Treeview(self.tab_pendientes, 
                                           columns=("id", "titulo", "categoria", "usuario", "fecha"), 
                                           show="headings")
        self.tree_pendientes.heading("id", text="ID")
        self.tree_pendientes.heading("titulo", text="Título")
        self.tree_pendientes.heading("categoria", text="Categoría")
        self.tree_pendientes.heading("usuario", text="Usuario")
        self.tree_pendientes.heading("fecha", text="Fecha")
        
        for col in self.tree_pendientes['columns']:
            self.tree_pendientes.column(col, width=150)
        
        self.tree_pendientes.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Botones de acción
        frame_botones = tk.Frame(self.tab_pendientes)
        frame_botones.pack(pady=10)
        
        btn_revisar = tk.Button(frame_botones, text="Revisar Noticia", command=self.revisar_noticia,
                               bg='#2196F3', fg='white')
        btn_revisar.pack(side='left', padx=5)
        
        btn_publicar = tk.Button(frame_botones, text="Publicar Seleccionada", command=self.publicar_noticia,
                                bg='#4CAF50', fg='white')
        btn_publicar.pack(side='left', padx=5)
        
        btn_rechazar = tk.Button(frame_botones, text="Rechazar Seleccionada", command=self.rechazar_noticia,
                                bg='#f44336', fg='white')
        btn_rechazar.pack(side='left', padx=5)
    
    def crear_lista_publicadas(self):
        # Treeview para noticias publicadas
        self.tree_publicadas = ttk.Treeview(self.tab_publicadas, 
                                           columns=("id", "titulo", "categoria", "visitas", "fecha"), 
                                           show="headings")
        self.tree_publicadas.heading("id", text="ID")
        self.tree_publicadas.heading("titulo", text="Título")
        self.tree_publicadas.heading("categoria", text="Categoría")
        self.tree_publicadas.heading("visitas", text="Visitas")
        self.tree_publicadas.heading("fecha", text="Fecha Publicación")
        
        for col in self.tree_publicadas['columns']:
            self.tree_publicadas.column(col, width=150)
        
        self.tree_publicadas.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Botones
        btn_ver = tk.Button(self.tab_publicadas, text="Ver Detalles", command=self.ver_noticia_publicada)
        btn_ver.pack(pady=5)
        
        # Cargar publicadas
        self.cargar_noticias_publicadas()
    
    def cargar_noticias_pendientes(self):
        # Limpiar treeview
        for item in self.tree_pendientes.get_children():
            self.tree_pendientes.delete(item)
        
        try:
            self.db.cur.execute("""
                SELECT n.id, n.titulo, n.categoria, u.username, 
                       TO_CHAR(n.fecha_creacion, 'DD/MM/YYYY HH24:MI') as fecha
                FROM noticias n
                JOIN usuarios u ON n.usuario_id = u.id
                WHERE n.estado = 'pendiente'
                ORDER BY n.fecha_creacion ASC
            """)
            
            for noticia in self.db.cur.fetchall():
                self.tree_pendientes.insert("", "end", values=noticia)
                
        except Exception as e:
            print(f"Error al cargar noticias pendientes: {e}")
    
    def cargar_noticias_publicadas(self):
        for item in self.tree_publicadas.get_children():
            self.tree_publicadas.delete(item)
        
        try:
            self.db.cur.execute("""
                SELECT id, titulo, categoria, visitas, 
                       TO_CHAR(fecha_publicacion, 'DD/MM/YYYY HH24:MI') as fecha
                FROM noticias
                WHERE estado = 'publicada'
                ORDER BY fecha_publicacion DESC
            """)
            
            for noticia in self.db.cur.fetchall():
                self.tree_publicadas.insert("", "end", values=noticia)
                
        except Exception as e:
            print(f"Error al cargar noticias publicadas: {e}")
    
    def revisar_noticia(self):
        seleccion = self.tree_pendientes.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione una noticia para revisar")
            return
        
        item = self.tree_pendientes.item(seleccion[0])
        noticia_id = item['values'][0]
        
        RevisarNoticiaWindow(self.db, noticia_id, self.usuario_id, self)
    
    def publicar_noticia(self):
        seleccion = self.tree_pendientes.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione una noticia para publicar")
            return
        
        item = self.tree_pendientes.item(seleccion[0])
        noticia_id = item['values'][0]
        
        try:
            self.db.cur.execute("""
                UPDATE noticias 
                SET estado = 'publicada', fecha_publicacion = CURRENT_TIMESTAMP, 
                    revisado_por = %s
                WHERE id = %s
            """, (self.usuario_id, noticia_id))
            self.db.conn.commit()
            
            messagebox.showinfo("Éxito", "Noticia publicada exitosamente")
            self.cargar_noticias_pendientes()
            self.cargar_noticias_publicadas()
            self.mostrar_estadisticas()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo publicar la noticia: {e}")
    
    def rechazar_noticia(self):
        seleccion = self.tree_pendientes.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione una noticia para rechazar")
            return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de rechazar esta noticia?"):
            item = self.tree_pendientes.item(seleccion[0])
            noticia_id = item['values'][0]
            
            try:
                self.db.cur.execute("""
                    UPDATE noticias 
                    SET estado = 'rechazada', revisado_por = %s
                    WHERE id = %s
                """, (self.usuario_id, noticia_id))
                self.db.conn.commit()
                
                messagebox.showinfo("Éxito", "Noticia rechazada")
                self.cargar_noticias_pendientes()
                
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo rechazar la noticia: {e}")
    
    def ver_noticia_publicada(self):
        seleccion = self.tree_publicadas.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione una noticia")
            return
        
        item = self.tree_publicadas.item(seleccion[0])
        noticia_id = item['values'][0]
        
        VerNoticiaPublicadaWindow(self.db, noticia_id)
    
    def mostrar_estadisticas(self):
        # Limpiar tab de estadísticas
        for widget in self.tab_estadisticas.winfo_children():
            widget.destroy()
        
        try:
            # Total de denuncias
            self.db.cur.execute("SELECT COUNT(*) FROM noticias")
            total = self.db.cur.fetchone()[0]
            
            # Por estado
            self.db.cur.execute("""
                SELECT estado, COUNT(*) FROM noticias GROUP BY estado
            """)
            estados = self.db.cur.fetchall()
            
            # Por categoría
            self.db.cur.execute("""
                SELECT categoria, COUNT(*) FROM noticias GROUP BY categoria
            """)
            categorias = self.db.cur.fetchall()
            
            # Mostrar estadísticas
            frame = tk.Frame(self.tab_estadisticas)
            frame.pack(pady=20, padx=20)
            
            tk.Label(frame, text="Estadísticas Generales", 
                    font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
            
            tk.Label(frame, text=f"Total de Denuncias: {total}", 
                    font=("Arial", 12)).grid(row=1, column=0, columnspan=2, pady=5, sticky='w')
            
            tk.Label(frame, text="\nPor Estado:", 
                    font=("Arial", 12, "bold")).grid(row=2, column=0, columnspan=2, pady=5, sticky='w')
            
            row = 3
            for estado, count in estados:
                tk.Label(frame, text=f"{estado}: {count}").grid(row=row, column=0, pady=2, sticky='w')
                row += 1
            
            tk.Label(frame, text="\nPor Categoría:", 
                    font=("Arial", 12, "bold")).grid(row=row, column=0, columnspan=2, pady=5, sticky='w')
            row += 1
            
            for categoria, count in categorias:
                tk.Label(frame, text=f"{categoria or 'Sin categoría'}: {count}").grid(row=row, column=0, pady=2, sticky='w')
                row += 1
                
        except Exception as e:
            print(f"Error al mostrar estadísticas: {e}")
    
    def cerrar_sesion(self):
        self.ventana.destroy()
        LoginWindow().run()

# Ventana para revisar noticia
class RevisarNoticiaWindow:
    def __init__(self, db, noticia_id, revisor_id, parent):
        self.db = db
        self.noticia_id = noticia_id
        self.revisor_id = revisor_id
        self.parent = parent
        self.ventana = tk.Toplevel()
        self.ventana.title("Revisar Noticia")
        self.ventana.geometry("600x500")
        
        self.cargar_noticia()
    
    def cargar_noticia(self):
        try:
            self.db.cur.execute("""
                SELECT n.titulo, n.contenido, n.categoria, n.ubicacion, 
                       n.evidencia_path, u.username, n.fecha_creacion
                FROM noticias n
                JOIN usuarios u ON n.usuario_id = u.id
                WHERE n.id = %s
            """, (self.noticia_id,))
            
            noticia = self.db.cur.fetchone()
            
            if noticia:
                # Mostrar datos
                frame = tk.Frame(self.ventana)
                frame.pack(pady=10, padx=10, fill='both', expand=True)
                
                tk.Label(frame, text="Título:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky='w', pady=5)
                tk.Label(frame, text=noticia[0]).grid(row=0, column=1, sticky='w', pady=5)
                
                tk.Label(frame, text="Categoría:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky='w', pady=5)
                tk.Label(frame, text=noticia[2]).grid(row=1, column=1, sticky='w', pady=5)
                
                tk.Label(frame, text="Ubicación:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky='w', pady=5)
                tk.Label(frame, text=noticia[3] or "No especificada").grid(row=2, column=1, sticky='w', pady=5)
                
                tk.Label(frame, text="Denunciante:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky='w', pady=5)
                tk.Label(frame, text=noticia[5]).grid(row=3, column=1, sticky='w', pady=5)
                
                tk.Label(frame, text="Fecha:", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky='w', pady=5)
                tk.Label(frame, text=noticia[6].strftime("%d/%m/%Y %H:%M")).grid(row=4, column=1, sticky='w', pady=5)
                
                tk.Label(frame, text="Contenido:", font=("Arial", 10, "bold")).grid(row=5, column=0, sticky='ne', pady=5)
                
                text_contenido = scrolledtext.ScrolledText(frame, width=50, height=10)
                text_contenido.grid(row=5, column=1, pady=5, padx=5)
                text_contenido.insert("1.0", noticia[1])
                text_contenido.config(state='disabled')
                
                if noticia[4]:
                    tk.Label(frame, text="Evidencia:", font=("Arial", 10, "bold")).grid(row=6, column=0, sticky='w', pady=5)
                    tk.Label(frame, text=noticia[4], fg='blue').grid(row=6, column=1, sticky='w', pady=5)
                
                # Botones
                frame_botones = tk.Frame(self.ventana)
                frame_botones.pack(pady=10)
                
                btn_publicar = tk.Button(frame_botones, text="Publicar", command=self.publicar,
                                       bg='#4CAF50', fg='white')
                btn_publicar.pack(side='left', padx=5)
                
                btn_rechazar = tk.Button(frame_botones, text="Rechazar", command=self.rechazar,
                                       bg='#f44336', fg='white')
                btn_rechazar.pack(side='left', padx=5)
                
                btn_cancelar = tk.Button(frame_botones, text="Cancelar", command=self.ventana.destroy)
                btn_cancelar.pack(side='left', padx=5)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar la noticia: {e}")
    
    def publicar(self):
        try:
            self.db.cur.execute("""
                UPDATE noticias 
                SET estado = 'publicada', fecha_publicacion = CURRENT_TIMESTAMP, 
                    revisado_por = %s
                WHERE id = %s
            """, (self.revisor_id, self.noticia_id))
            self.db.conn.commit()
            
            messagebox.showinfo("Éxito", "Noticia publicada exitosamente")
            self.parent.cargar_noticias_pendientes()
            self.parent.cargar_noticias_publicadas()
            self.parent.mostrar_estadisticas()
            self.ventana.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo publicar: {e}")
    
    def rechazar(self):
        if messagebox.askyesno("Confirmar", "¿Está seguro de rechazar esta noticia?"):
            try:
                self.db.cur.execute("""
                    UPDATE noticias 
                    SET estado = 'rechazada', revisado_por = %s
                    WHERE id = %s
                """, (self.revisor_id, self.noticia_id))
                self.db.conn.commit()
                
                messagebox.showinfo("Éxito", "Noticia rechazada")
                self.parent.cargar_noticias_pendientes()
                self.parent.mostrar_estadisticas()
                self.ventana.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo rechazar: {e}")

# Ventana para ver detalles de noticia
class DetallesNoticiaWindow:
    def __init__(self, db, noticia_id, usuario_id):
        self.db = db
        self.noticia_id = noticia_id
        self.usuario_id = usuario_id
        self.ventana = tk.Toplevel()
        self.ventana.title("Detalles de la Denuncia")
        self.ventana.geometry("600x500")
        
        self.cargar_detalles()
    
    def cargar_detalles(self):
        try:
            self.db.cur.execute("""
                SELECT titulo, contenido, categoria, ubicacion, estado, 
                       evidencia_path, fecha_creacion
                FROM noticias
                WHERE id = %s
            """, (self.noticia_id,))
            
            noticia = self.db.cur.fetchone()
            
            if noticia:
                frame = tk.Frame(self.ventana)
                frame.pack(pady=10, padx=10, fill='both', expand=True)
                
                tk.Label(frame, text="Título:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky='w', pady=5)
                tk.Label(frame, text=noticia[0]).grid(row=0, column=1, sticky='w', pady=5)
                
                tk.Label(frame, text="Categoría:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky='w', pady=5)
                tk.Label(frame, text=noticia[2] or "Sin categoría").grid(row=1, column=1, sticky='w', pady=5)
                
                tk.Label(frame, text="Ubicación:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky='w', pady=5)
                tk.Label(frame, text=noticia[3] or "No especificada").grid(row=2, column=1, sticky='w', pady=5)
                
                tk.Label(frame, text="Estado:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky='w', pady=5)
                
                estado_color = {
                    'pendiente': 'orange',
                    'publicada': 'green',
                    'rechazada': 'red'
                }
                estado = noticia[4]
                label_estado = tk.Label(frame, text=estado.upper(), fg=estado_color.get(estado, 'black'))
                label_estado.grid(row=3, column=1, sticky='w', pady=5)
                
                tk.Label(frame, text="Fecha:", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky='w', pady=5)
                tk.Label(frame, text=noticia[6].strftime("%d/%m/%Y %H:%M")).grid(row=4, column=1, sticky='w', pady=5)
                
                tk.Label(frame, text="Contenido:", font=("Arial", 10, "bold")).grid(row=5, column=0, sticky='ne', pady=5)
                
                text_contenido = scrolledtext.ScrolledText(frame, width=50, height=10)
                text_contenido.grid(row=5, column=1, pady=5, padx=5)
                text_contenido.insert("1.0", noticia[1])
                text_contenido.config(state='disabled')
                
                if noticia[5]:
                    tk.Label(frame, text="Evidencia:", font=("Arial", 10, "bold")).grid(row=6, column=0, sticky='w', pady=5)
                    tk.Label(frame, text=noticia[5], fg='blue').grid(row=6, column=1, sticky='w', pady=5)
                
                btn_cerrar = tk.Button(self.ventana, text="Cerrar", command=self.ventana.destroy)
                btn_cerrar.pack(pady=10)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar detalles: {e}")

# Ventana para ver noticia publicada
class VerNoticiaPublicadaWindow:
    def __init__(self, db, noticia_id):
        self.db = db
        self.noticia_id = noticia_id
        self.ventana = tk.Toplevel()
        self.ventana.title("Noticia Publicada")
        self.ventana.geometry("700x600")
        
        self.cargar_noticia()
        self.incrementar_visitas()
    
    def incrementar_visitas(self):
        try:
            self.db.cur.execute("""
                UPDATE noticias SET visitas = visitas + 1 WHERE id = %s
            """, (self.noticia_id,))
            self.db.conn.commit()
            
        except Exception as e:
            print(f"Error al incrementar visitas: {e}")
    
    def cargar_noticia(self):
        try:
            self.db.cur.execute("""
                SELECT n.titulo, n.contenido, n.categoria, n.ubicacion, 
                       n.visitas, u.username, n.fecha_publicacion
                FROM noticias n
                JOIN usuarios u ON n.usuario_id = u.id
                WHERE n.id = %s
            """, (self.noticia_id,))
            
            noticia = self.db.cur.fetchone()
            
            if noticia:
                frame = tk.Frame(self.ventana)
                frame.pack(pady=10, padx=10, fill='both', expand=True)
                
                tk.Label(frame, text=noticia[0], font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
                
                tk.Label(frame, text=f"Categoría: {noticia[2]}", font=("Arial", 10)).grid(row=1, column=0, sticky='w', pady=5)
                tk.Label(frame, text=f"Visitas: {noticia[4]}", font=("Arial", 10)).grid(row=1, column=1, sticky='e', pady=5)
                
                tk.Label(frame, text=f"Ubicación: {noticia[3] or 'No especificada'}", font=("Arial", 10)).grid(row=2, column=0, sticky='w', pady=5)
                tk.Label(frame, text=f"Publicado por: {noticia[5]}", font=("Arial", 10)).grid(row=2, column=1, sticky='e', pady=5)
                
                tk.Label(frame, text=f"Fecha: {noticia[6].strftime('%d/%m/%Y %H:%M')}", font=("Arial", 10)).grid(row=3, column=0, columnspan=2, sticky='w', pady=5)
                
                tk.Label(frame, text="Contenido:", font=("Arial", 12, "bold")).grid(row=4, column=0, sticky='w', pady=10)
                
                text_contenido = scrolledtext.ScrolledText(frame, width=70, height=15)
                text_contenido.grid(row=5, column=0, columnspan=2, pady=5, padx=5)
                text_contenido.insert("1.0", noticia[1])
                text_contenido.config(state='disabled')
                
                btn_cerrar = tk.Button(self.ventana, text="Cerrar", command=self.ventana.destroy)
                btn_cerrar.pack(pady=10)
                
                # Sección de comentarios (opcional)
                self.cargar_comentarios()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar noticia: {e}")
    
    def cargar_comentarios(self):
        # Aquí se puede implementar la sección de comentarios si se desea
        pass

# Ejecutar la aplicación
if __name__ == "__main__":
    app = LoginWindow()
    app.run()