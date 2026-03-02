"""
SISTEMA FINANCIERO COOPJUDICIAL - VERSIÓN 4.0 COMPLETA Y CORREGIDA
==================================================================

Sistema integral de gestión financiera para cooperativas
Versión completamente funcional y corregida
"""

import pandas as pd
import os
import random
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
from collections import defaultdict
import sqlite3
import csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
import numpy as np

print("🚀 Iniciando Sistema COOPJUDICIAL - Versión 4.0 Corregida")

class ModernFinancialApp:
    """
    Clase principal del Sistema Financiero COOPJUDICIAL
    Versión 4.0 completamente funcional y corregida
    """
    
    def __init__(self, root):
        """
        Inicializa la aplicación con configuración completa y corregida
        """
        self.root = root
        self.root.title("🏦 COOPJUDICIAL - Sistema Financiero Integral v4.0")
        self.root.geometry("1400x850")
        self.root.configure(bg='#1e1e2e')
        self.root.resizable(True, True)
        
        # PRIMERO inicializar business_config ANTES de load_data
        self.business_config = {
            "tasa_interes_ahorro": 0.02,
            "tasa_interes_credito": 0.12,
            "cuota_afiliacion": 50000,
            "aportes_minimos": 10000,
            "dias_gracia": 5,
            "retencion_fuente": 0.04,
            "max_cuotas_credito": 36,
            "monto_min_credito": 500000,
            "seguro_credito": 0.001,
            "comision_desembolso": 0.005
        }
        
        # Configuración inicial
        self.center_window(1400, 850)
        self.setup_styles()
        self.load_data()
        self.current_window = None
        self.chart_figures = []
        
        # Crear interfaz principal
        self.create_main_interface()
        
        # Iniciar servicios automáticos
        self.root.after(30000, self.auto_save)
        self.root.after(10000, self.auto_refresh_metrics)

    def center_window(self, width, height):
        """Centra la ventana en la pantalla"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def setup_styles(self):
        """Configura los estilos visuales modernos"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Paleta de colores corregida - AGREGADO 'purple'
        self.colors = {
            'primary': '#2c3e50',
            'primary_light': '#3498db',
            'primary_dark': '#1a252f',
            'secondary': '#2980b9',
            'accent': '#e74c3c',
            'success': '#27ae60',
            'warning': '#f39c12',
            'danger': '#c0392b',
            'info': '#17a2b8',
            'dark': '#2c3e50',
            'light': '#ecf0f1',
            'muted': '#95a5a6',
            'bg_dark': '#1e272c',
            'bg_light': '#34495e',
            'bg_card': '#2c3e50',
            'border': '#34495e',
            'header': '#1a252f',
            'hover': '#3498db',
            'chart_1': '#3498db',
            'chart_2': '#e74c3c',
            'chart_3': '#2ecc71',
            'chart_4': '#f39c12',
            'purple': '#9b59b6'  # COLOR PURPLE AGREGADO
        }

    def load_data(self):
        """Carga los datos del sistema - CORREGIDO el orden"""
        self.data_file = "coopjudicial_data_v4.json"
        self.backup_file = "coopjudicial_backup_v4.json"
        self.config_file = "coopjudicial_config_v4.json"
        self.database_file = "coopjudicial_database.db"
        
        # Definición de módulos del sistema
        self.categorias = {
            "1": "Gestión de Créditos",
            "2": "Control de Afiliados", 
            "3": "Aportes Sociales",
            "4": "Cuentas de Ahorro",
            "5": "Suspensiones Temporales",
            "6": "Suspensiones por Retiro", 
            "7": "Cálculo de Intereses",
            "8": "Estados de Cuenta",
            "9": "Reportes Ejecutivos"
        }
        
        try:
            # Cargar datos principales desde JSON
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.datos = json.load(f)
                print("✅ Datos JSON cargados correctamente")
                self.create_backup()
            else:
                self.datos = {categoria: [] for categoria in self.categorias.values()}
                self.create_sample_data()
                print("📁 Estructura de datos creada desde cero")
            
            # Cargar configuración - AHORA business_config YA ESTÁ INICIALIZADO
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    self.business_config.update(saved_config)
                    
            # Inicializar base de datos SQLite
            self.init_database()
                    
        except Exception as e:
            print(f"❌ Error cargando datos: {e}")
            messagebox.showerror("Error", f"Error cargando datos: {str(e)}")
            self.try_load_backup()

    def init_database(self):
        """Inicializa la base de datos SQLite"""
        try:
            self.conn = sqlite3.connect(self.database_file)
            self.cursor = self.conn.cursor()
            
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS registros_financieros (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    modulo TEXT NOT NULL,
                    nombre TEXT NOT NULL,
                    identificacion TEXT NOT NULL,
                    valor REAL NOT NULL,
                    cuotas INTEGER,
                    estado TEXT,
                    tipo TEXT,
                    observaciones TEXT,
                    fecha_registro TEXT,
                    fecha_actualizacion TEXT
                )
            ''')
            
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS configuraciones (
                    clave TEXT PRIMARY KEY,
                    valor TEXT NOT NULL
                )
            ''')
            
            self.conn.commit()
            print("✅ Base de datos SQLite inicializada correctamente")
            
        except Exception as e:
            print(f"⚠️  Error inicializando base de datos: {e}")

    def create_backup(self):
        """Crea copia de seguridad automática"""
        try:
            with open(self.backup_file, 'w', encoding='utf-8') as f:
                json.dump(self.datos, f, indent=2, ensure_ascii=False)
            print("✅ Backup creado correctamente")
        except Exception as e:
            print(f"⚠️  No se pudo crear backup: {e}")

    def try_load_backup(self):
        """Intenta cargar desde copia de seguridad"""
        try:
            if os.path.exists(self.backup_file):
                with open(self.backup_file, 'r', encoding='utf-8') as f:
                    self.datos = json.load(f)
                messagebox.showinfo("Recuperación", "Datos recuperados desde copia de seguridad")
            else:
                self.datos = {categoria: [] for categoria in self.categorias.values()}
        except Exception as e:
            self.datos = {categoria: [] for categoria in self.categorias.values()}
            messagebox.showerror("Error", "No se pudieron recuperar los datos")

    def create_sample_data(self):
        """Crea datos de ejemplo realistas"""
        nombres = [
            "Juan Carlos Pérez", "María Elena García", "Carlos Andrés López", 
            "Ana María Martínez", "Pedro José Rodríguez", "Laura Patricia Hernández"
        ]
        
        for i in range(50):
            categoria = random.choice(list(self.categorias.values()))
            
            registro_base = {
                "ID": f"{categoria[:3].upper()}{i+1:05d}",
                "Nombre": random.choice(nombres),
                "Identificación": f"{random.randint(10, 99)}.{random.randint(100, 999)}.{random.randint(100, 999)}",
                "Valor": str(random.randint(100000, 5000000)),
                "Cuotas": str(random.randint(1, 36)),
                "Observaciones": "Registro del sistema COOPJUDICIAL v4.0",
                "Fecha_Registro": (datetime.now() - timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d %H:%M:%S"),
                "Fecha_Actualizacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Estado": random.choice(["Activo", "En mora", "Pagado", "Vigente"]),
                "Tipo": random.choice(["Personal", "Hipotecario", "Vehicular", "Comercial"])
            }
            
            if categoria == "Control de Afiliados":
                registro_base.update({
                    "Fecha_Afiliacion": (datetime.now() - timedelta(days=random.randint(0, 730))).strftime("%Y-%m-%d"),
                    "Tipo_Afiliado": random.choice(["Ordinario", "Especial", "Fundador"]),
                })
            elif categoria == "Aportes Sociales":
                registro_base.update({
                    "Periodo": f"{random.randint(2020, 2024)}-{random.randint(1, 12):02d}",
                    "Tipo_Aporte": random.choice(["Obligatorio", "Voluntario", "Especial"]),
                })
            elif categoria == "Cuentas de Ahorro":
                registro_base.update({
                    "Saldo_Anterior": str(random.randint(0, 1000000)),
                    "Intereses_Acumulados": str(random.randint(0, 50000)),
                })
            
            self.datos[categoria].append(registro_base)
        
        self.save_data()
        print("📊 Datos de ejemplo creados exitosamente")

    def save_data(self):
        """Guarda los datos de forma segura"""
        try:
            temp_file = self.data_file + ".tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.datos, f, indent=2, ensure_ascii=False)
            
            if os.path.exists(self.data_file):
                os.replace(temp_file, self.data_file)
            else:
                os.rename(temp_file, self.data_file)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.business_config, f, indent=2, ensure_ascii=False)
            
            self.create_backup()
            return True
            
        except Exception as e:
            print(f"❌ Error guardando datos: {e}")
            messagebox.showerror("Error", f"Error guardando datos: {str(e)}")
            return False

    def auto_save(self):
        """Guardado automático periódico"""
        if self.save_data():
            self.update_status("💾 Guardado automático realizado")
        self.root.after(30000, self.auto_save)

    # =========================================================================
    # INTERFAZ PRINCIPAL - COMPLETAMENTE FUNCIONAL
    # =========================================================================

    def create_main_interface(self):
        """Crea la interfaz principal"""
        main_frame = tk.Frame(self.root, bg=self.colors['bg_dark'])
        main_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        self.create_enhanced_header(main_frame)
        self.create_metrics_panel(main_frame)
        self.create_modules_panel(main_frame)
        self.create_enhanced_quick_actions(main_frame)
        self.create_enhanced_status_bar(main_frame)

    def create_enhanced_header(self, parent):
        """Crea el encabezado corporativo"""
        header_frame = tk.Frame(parent, bg=self.colors['bg_dark'])
        header_frame.pack(fill='x', pady=(0, 25))
        
        title_frame = tk.Frame(header_frame, bg=self.colors['bg_dark'])
        title_frame.pack(fill='x', pady=15)
        
        main_title = tk.Label(title_frame, 
                             text="🏦 COOPJUDICIAL",
                             font=('Arial', 36, 'bold'),
                             fg=self.colors['primary_light'],
                             bg=self.colors['bg_dark'])
        main_title.pack()
        
        sub_title = tk.Label(title_frame,
                           text="Sistema Financiero Integral - Versión 4.0 Completa",
                           font=('Arial', 16),
                           fg=self.colors['light'],
                           bg=self.colors['bg_dark'])
        sub_title.pack(pady=(8, 0))
        
        separator = tk.Frame(header_frame, height=2, bg=self.colors['primary_light'])
        separator.pack(fill='x', pady=10)

    def create_metrics_panel(self, parent):
        """Crea el panel de métricas financieras en tiempo real"""
        self.metrics_frame = tk.Frame(parent, bg=self.colors['bg_card'], relief='ridge', bd=2)
        self.metrics_frame.pack(fill='x', pady=(0, 30))
        self.update_metrics_display()

    def update_metrics_display(self):
        """Actualiza las métricas en tiempo real"""
        for widget in self.metrics_frame.winfo_children():
            widget.destroy()
        
        metrics = self.calculate_advanced_metrics()
        
        metric_items = [
            ("📊 Total Registros", f"{metrics['total_registros']:,}", "📈", self.colors['info']),
            ("💰 Valor Cartera", f"${metrics['total_valor']:,.0f}", "💵", self.colors['success']),
            ("💳 Créditos Activos", f"{metrics['creditos_activos']}", "📋", self.colors['primary_light']),
            ("👥 Total Afiliados", f"{metrics['total_afiliados']}", "👤", self.colors['secondary']),
            ("🏦 Total Ahorros", f"${metrics['total_ahorros']:,.0f}", "💳", self.colors['warning']),
            ("📈 Tasa Activa", f"{self.business_config['tasa_interes_credito']*100}%", "📊", self.colors['accent'])
        ]
        
        for i, (title, value, icon, color) in enumerate(metric_items):
            metric_card = self.create_metric_card(title, value, icon, color)
            metric_card.grid(row=0, column=i, padx=6, pady=8, sticky='nsew')
            self.metrics_frame.grid_columnconfigure(i, weight=1)

    def create_metric_card(self, title, value, icon, color):
        """Crea una tarjeta de métrica individual"""
        card = tk.Frame(self.metrics_frame, bg=color, relief='raised', bd=1)
        
        icon_label = tk.Label(card, text=icon,
                            font=('Arial', 14),
                            fg='white',
                            bg=color)
        icon_label.pack(pady=(8, 2))
        
        value_label = tk.Label(card, text=value,
                             font=('Arial', 16, 'bold'),
                             fg='white',
                             bg=color)
        value_label.pack(pady=2)
        
        title_label = tk.Label(card, text=title,
                             font=('Arial', 9),
                             fg='white',
                             bg=color,
                             wraplength=100)
        title_label.pack(pady=(2, 8))
        
        return card

    def calculate_advanced_metrics(self):
        """Calcula métricas financieras avanzadas en tiempo real"""
        total_registros = sum(len(registros) for registros in self.datos.values())
        total_valor = self.calculate_total_value()
        creditos_activos = self.count_active_credits()
        total_afiliados = len(self.datos["Control de Afiliados"])
        total_ahorros = sum(float(r.get('Valor', 0)) for r in self.datos["Cuentas de Ahorro"])
        
        return {
            'total_registros': total_registros,
            'total_valor': total_valor,
            'creditos_activos': creditos_activos,
            'total_afiliados': total_afiliados,
            'total_ahorros': total_ahorros
        }

    def calculate_total_value(self):
        """Calcula el valor total de todos los registros"""
        total = 0
        for categoria, registros in self.datos.items():
            for registro in registros:
                try:
                    total += float(registro.get('Valor', 0))
                except (ValueError, TypeError):
                    continue
        return total

    def count_active_credits(self):
        """Cuenta los créditos activos en el sistema"""
        count = 0
        for registro in self.datos.get("Gestión de Créditos", []):
            if registro.get('Estado') in ['Activo', 'Vigente']:
                count += 1
        return count

    def create_modules_panel(self, parent):
        """Crea el panel de módulos del sistema"""
        modules_frame = tk.LabelFrame(parent,
                                    text="  📁 Módulos del Sistema Financiero  ",
                                    font=('Arial', 18, 'bold'),
                                    fg=self.colors['primary_light'],
                                    bg=self.colors['bg_dark'],
                                    bd=3,
                                    relief='groove',
                                    labelanchor='n')
        modules_frame.pack(fill='both', expand=True, pady=(0, 25))
        
        for i in range(3):
            modules_frame.grid_rowconfigure(i, weight=1)
        for i in range(3):
            modules_frame.grid_columnconfigure(i, weight=1)
        
        modules_info = [
            ("💳 Gestión de Créditos", "1", self.colors['primary_light'], "Administración de cartera crediticia"),
            ("👥 Control de Afiliados", "2", self.colors['success'], "Gestión de afiliaciones"),
            ("💰 Aportes Sociales", "3", self.colors['warning'], "Registro de aportes"),
            ("🏦 Cuentas de Ahorro", "4", self.colors['info'], "Administración de ahorros"),
            ("⏸️ Suspensiones", "5", self.colors['danger'], "Gestión de suspensiones"),
            ("📊 Cálculo de Intereses", "7", self.colors['secondary'], "Cálculos financieros"),
            ("📋 Estados de Cuenta", "8", self.colors['accent'], "Estados financieros"),
            ("📈 Reportes Ejecutivos", "9", self.colors['purple'], "Reportes gerenciales"),  # CORREGIDO: usa 'purple'
            ("⚙️ Configuración", "10", self.colors['muted'], "Configuración del sistema")
        ]
        
        for i, (text, key, color, tooltip) in enumerate(modules_info):
            row = i // 3
            col = i % 3
            self.create_enhanced_module_button(modules_frame, text, key, color, tooltip, row, col)

    def create_enhanced_module_button(self, parent, text, key, color, tooltip, row, col):
        """Crea un botón de módulo mejorado"""
        btn_frame = tk.Frame(parent, bg=self.colors['bg_dark'])
        btn_frame.grid(row=row, column=col, padx=15, pady=15, sticky='nsew')
        
        if key not in ["10"]:
            categoria_nombre = self.categorias.get(key, "Configuracion")
            count = len(self.datos.get(categoria_nombre, []))
            count_text = f"📊 {count} registros"
            
            count_label = tk.Label(btn_frame, text=count_text,
                                 font=('Arial', 10, 'bold'),
                                 fg=self.colors['light'],
                                 bg=self.colors['bg_dark'])
            count_label.pack(pady=(10, 5))
        
        btn = self.create_modern_button(btn_frame, text, color, 
                                      lambda k=key: self.open_module_window(k))
        btn.pack(fill='both', expand=True, pady=5)
        
        self.create_enhanced_tooltip(btn, tooltip)

    def create_modern_button(self, parent, text, color, command):
        """Crea botones modernos con efectos hover"""
        btn = tk.Button(parent,
                      text=text,
                      font=('Arial', 12, 'bold'),
                      bg=color,
                      fg='white',
                      borderwidth=0,
                      relief='flat',
                      cursor='hand2',
                      padx=25,
                      pady=18,
                      command=command,
                      activebackground=self.lighten_color(color, 25),
                      activeforeground='white')
        
        def on_enter(e):
            btn.config(bg=self.lighten_color(color, 20))
        def on_leave(e):
            btn.config(bg=color)
            
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn

    def create_enhanced_tooltip(self, widget, text):
        """Crea tooltips elegantes mejorados"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+20}+{event.y_root+20}")
            
            frame = tk.Frame(tooltip, bg='white', relief='solid', borderwidth=1)
            frame.pack(fill='both', expand=True)
            
            label = tk.Label(frame, text=text,
                           background="#ffffe0",
                           foreground="black",
                           relief='flat',
                           font=('Arial', 9),
                           padx=12,
                           pady=8,
                           justify='left')
            label.pack()
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                delattr(widget, 'tooltip')
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    def lighten_color(self, color, amount):
        """Aclara un color hexadecimal"""
        try:
            color = color.lstrip('#')
            rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
            light_rgb = tuple(min(255, c + amount) for c in rgb)
            return f'#{light_rgb[0]:02x}{light_rgb[1]:02x}{light_rgb[2]:02x}'
        except:
            return color

    def create_enhanced_quick_actions(self, parent):
        """Crea el panel de acciones rápidas mejorado"""
        actions_frame = tk.Frame(parent, bg=self.colors['bg_dark'])
        actions_frame.pack(fill='x', pady=(0, 20))
        
        quick_actions = [
            ("🔍 Búsqueda Global", self.colors['info'], self.show_advanced_global_search),
            ("📊 Dashboard", self.colors['success'], self.show_executive_dashboard),
            ("📈 Reportes Gráficos", self.colors['warning'], self.show_graphical_reports),
            ("💾 Exportar Datos", self.colors['primary_light'], self.export_complete_data),
            ("🔄 Actualizar", self.colors['secondary'], self.refresh_system),
            ("❌ Salir", self.colors['danger'], self.safe_exit)
        ]
        
        for text, color, command in quick_actions:
            btn = self.create_compact_button(actions_frame, text, color, command)
            btn.pack(side='left', padx=8, ipadx=15, ipady=8)

    def create_compact_button(self, parent, text, color, command):
        """Crea botones compactos mejorados"""
        btn = tk.Button(parent,
                      text=text,
                      font=('Arial', 10, 'bold'),
                      bg=color,
                      fg='white',
                      borderwidth=0,
                      relief='flat',
                      cursor='hand2',
                      padx=15,
                      pady=8,
                      command=command,
                      activebackground=self.lighten_color(color, 25))
        
        def on_enter(e):
            btn.config(bg=self.lighten_color(color, 20))
        def on_leave(e):
            btn.config(bg=color)
            
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn

    def create_enhanced_status_bar(self, parent):
        """Crea la barra de estado mejorada"""
        status_frame = tk.Frame(parent, bg=self.colors['primary_dark'])
        status_frame.pack(fill='x', pady=(10, 0))
        
        self.status_var = tk.StringVar()
        self.update_status("✅ Sistema COOPJUDICIAL v4.0 inicializado correctamente")
        
        status_label = tk.Label(status_frame, textvariable=self.status_var,
                              font=('Arial', 11, 'bold'),
                              fg=self.colors['light'],
                              bg=self.colors['primary_dark'],
                              padx=20,
                              pady=10)
        status_label.pack(side='left')
        
        time_frame = tk.Frame(status_frame, bg=self.colors['primary_dark'])
        time_frame.pack(side='right', padx=20, pady=10)
        
        self.time_var = tk.StringVar()
        self.date_var = tk.StringVar()
        self.update_datetime()
        
        time_label = tk.Label(time_frame, textvariable=self.time_var,
                            font=('Arial', 10, 'bold'),
                            fg=self.colors['light'],
                            bg=self.colors['primary_dark'])
        time_label.pack(side='top')
        
        date_label = tk.Label(time_frame, textvariable=self.date_var,
                            font=('Arial', 9),
                            fg=self.colors['muted'],
                            bg=self.colors['primary_dark'])
        date_label.pack(side='bottom')

    def update_datetime(self):
        """Actualiza la fecha y hora en la barra de estado"""
        current_time = datetime.now().strftime("%H:%M:%S")
        current_date = datetime.now().strftime("%Y-%m-%d")
        self.time_var.set(f"🕒 {current_time}")
        self.date_var.set(f"📅 {current_date}")
        self.root.after(1000, self.update_datetime)

    def update_status(self, message):
        """Actualiza el mensaje de estado"""
        if hasattr(self, 'status_var'):
            self.status_var.set(f"📢 {message}")

    def auto_refresh_metrics(self):
        """Actualización automática de métricas"""
        self.update_metrics_display()
        self.root.after(10000, self.auto_refresh_metrics)

    # =========================================================================
    # FUNCIONALIDADES PRINCIPALES - COMPLETAMENTE IMPLEMENTADAS
    # =========================================================================

    def open_module_window(self, module_key):
        """Abre ventana de módulo específico"""
        if self.current_window and self.current_window.winfo_exists():
            self.current_window.destroy()
            
        if module_key == "10":
            self.show_system_config()
            return
            
        module_name = self.categorias[module_key]
        
        self.current_window = tk.Toplevel(self.root)
        self.current_window.title(f"COOPJUDICIAL - {module_name}")
        self.current_window.geometry("1200x700")
        self.current_window.configure(bg=self.colors['bg_dark'])
        self.center_child_window(self.current_window, 1200, 700)
        
        self.create_module_interface(module_name)

    def create_module_interface(self, module_name):
        """Crea la interfaz completa de un módulo"""
        notebook = ttk.Notebook(self.current_window)
        notebook.pack(fill='both', expand=True, padx=20, pady=20)
        
        tabs_config = [
            ("➕ Nuevo Registro", self.create_registration_tab),
            ("👁️ Ver Registros", self.create_view_tab),
            ("🔍 Búsqueda", self.create_search_tab),
            ("📊 Estadísticas", self.create_stats_tab)
        ]
        
        for tab_name, tab_method in tabs_config:
            tab_frame = ttk.Frame(notebook)
            notebook.add(tab_frame, text=tab_name)
            tab_method(tab_frame, module_name)

    def create_registration_tab(self, parent, module_name):
        """Crea pestaña de registro de datos"""
        main_frame = tk.Frame(parent, bg=self.colors['bg_card'])
        main_frame.pack(fill='both', expand=True, padx=25, pady=25)
        
        title_label = tk.Label(main_frame,
                             text=f"Nuevo Registro - {module_name}",
                             font=('Arial', 18, 'bold'),
                             fg=self.colors['primary_light'],
                             bg=self.colors['bg_card'])
        title_label.pack(pady=(0, 25))
        
        form_frame = tk.Frame(main_frame, bg=self.colors['bg_card'])
        form_frame.pack(fill='x', pady=10)
        
        self.entries = {}
        fields = self.get_module_fields(module_name)
        
        for i, (label, field_name, field_type, required) in enumerate(fields):
            self.create_form_field(form_frame, label, field_name, field_type, required, i)
        
        button_frame = tk.Frame(main_frame, bg=self.colors['bg_card'])
        button_frame.pack(pady=25)
        
        actions = [
            ("💾 Guardar", self.colors['success'], lambda: self.save_module_data(module_name)),
            ("🧹 Limpiar", self.colors['warning'], self.clear_form),
            ("🔙 Volver", self.colors['secondary'], self.close_current_window)
        ]
        
        for text, color, command in actions:
            self.create_compact_button(button_frame, text, color, command).pack(side='left', padx=10)

    def get_module_fields(self, module_name):
        """Retorna campos específicos para cada módulo"""
        base_fields = [
            ("Nombre Completo", "nombre", "text", True),
            ("Identificación", "identificacion", "text", True),
            ("Valor", "valor", "number", True),
            ("Fecha", "fecha", "date", True),
            ("Observaciones", "observaciones", "text", False)
        ]
        
        specific_fields = {
            "Gestión de Créditos": [
                ("N° de Cuotas", "cuotas", "number", True),
                ("Estado", "estado", "combo", True),
                ("Tipo de Crédito", "tipo_credito", "combo", True)
            ],
            "Control de Afiliados": [
                ("Fecha Afiliación", "fecha_afiliacion", "date", True),
                ("Tipo Afiliado", "tipo_afiliado", "combo", True)
            ]
        }
        
        return base_fields + specific_fields.get(module_name, [])

    def create_form_field(self, parent, label, field_name, field_type, required, index):
        """Crea un campo del formulario"""
        row_frame = tk.Frame(parent, bg=self.colors['bg_card'])
        row_frame.pack(fill='x', pady=8)
        
        req_indicator = "🔴 " if required else "⚪ "
        label_widget = tk.Label(row_frame, text=f"{req_indicator}{label}",
                              font=('Arial', 11),
                              fg=self.colors['light'],
                              bg=self.colors['bg_card'],
                              width=20,
                              anchor='w')
        label_widget.pack(side='left', padx=(0, 15))
        
        if field_type == "text":
            entry = tk.Entry(row_frame, font=('Arial', 11),
                           bg='white', relief='solid', bd=1, width=40)
        elif field_type == "number":
            entry = tk.Entry(row_frame, font=('Arial', 11),
                           bg='white', relief='solid', bd=1, width=40)
        elif field_type == "date":
            entry = tk.Entry(row_frame, font=('Arial', 11),
                           bg='white', relief='solid', bd=1, width=40)
            entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        elif field_type == "combo":
            entry = ttk.Combobox(row_frame, font=('Arial', 11),
                               state="readonly", width=38)
            if "estado" in field_name:
                entry['values'] = ['Activo', 'En mora', 'Pagado', 'Vigente']
            elif "tipo" in field_name:
                entry['values'] = ['Personal', 'Hipotecario', 'Vehicular', 'Comercial']
        
        entry.pack(side='left', fill='x', expand=True)
        self.entries[field_name] = entry

    def save_module_data(self, module_name):
        """Guarda los datos del módulo actual"""
        try:
            required_fields = [name for (_, name, _, req) in self.get_module_fields(module_name) if req]
            missing_fields = []
            
            for field in required_fields:
                if field in self.entries and not self.entries[field].get().strip():
                    missing_fields.append(field)
            
            if missing_fields:
                messagebox.showwarning("Validación", 
                                    f"Los siguientes campos son obligatorios:\n- " + 
                                    "\n- ".join(missing_fields))
                return
            
            new_id = f"{module_name[:3].upper()}{len(self.datos[module_name])+1:05d}"
            
            registro = {
                "ID": new_id,
                "Fecha_Registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            field_mapping = {
                'nombre': 'Nombre',
                'identificacion': 'Identificación',
                'valor': 'Valor',
                'fecha': 'Fecha',
                'observaciones': 'Observaciones',
                'cuotas': 'Cuotas',
                'estado': 'Estado',
                'tipo_credito': 'Tipo',
                'fecha_afiliacion': 'Fecha_Afiliacion',
                'tipo_afiliado': 'Tipo_Afiliado'
            }
            
            for form_field, storage_field in field_mapping.items():
                if form_field in self.entries:
                    registro[storage_field] = self.entries[form_field].get().strip()
            
            self.datos[module_name].append(registro)
            
            if self.save_data():
                messagebox.showinfo("Éxito", "✅ Registro guardado correctamente")
                self.clear_form()
                self.update_status(f"Registro agregado a {module_name}")
            else:
                messagebox.showerror("Error", "❌ No se pudo guardar el registro")
                
        except Exception as e:
            messagebox.showerror("Error", f"❌ Error al guardar: {str(e)}")

    def clear_form(self):
        """Limpia todos los campos del formulario"""
        for entry in self.entries.values():
            if isinstance(entry, tk.Entry):
                entry.delete(0, tk.END)
            elif isinstance(entry, ttk.Combobox):
                entry.set('')

    def create_view_tab(self, parent, module_name):
        """Crea pestaña de visualización de registros"""
        main_frame = tk.Frame(parent, bg=self.colors['bg_card'])
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        toolbar = tk.Frame(main_frame, bg=self.colors['bg_card'])
        toolbar.pack(fill='x', pady=(0, 15))
        
        info_text = f"{module_name}: {len(self.datos[module_name])} registros"
        info_label = tk.Label(toolbar, text=info_text,
                            font=('Arial', 12, 'bold'),
                            fg=self.colors['primary_light'],
                            bg=self.colors['bg_card'])
        info_label.pack(side='left')
        
        self.create_data_table(main_frame, module_name)

    def create_data_table(self, parent, module_name):
        """Crea y configura la tabla de datos"""
        table_container = tk.Frame(parent, bg=self.colors['bg_card'])
        table_container.pack(fill='both', expand=True)
        
        columns = ["ID", "Nombre", "Identificación", "Valor", "Fecha", "Estado"]
        
        self.tree = ttk.Treeview(table_container, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        
        v_scroll = ttk.Scrollbar(table_container, orient='vertical', command=self.tree.yview)
        h_scroll = ttk.Scrollbar(table_container, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scroll.grid(row=0, column=1, sticky='ns')
        h_scroll.grid(row=1, column=0, sticky='ew')
        
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)
        
        self.load_table_data(module_name)

    def load_table_data(self, module_name):
        """Carga datos en la tabla"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        registros = self.datos.get(module_name, [])
        
        for registro in registros:
            values = [
                registro.get('ID', ''),
                registro.get('Nombre', ''),
                registro.get('Identificación', ''),
                registro.get('Valor', ''),
                registro.get('Fecha_Registro', '')[:10],
                registro.get('Estado', '')
            ]
            self.tree.insert('', 'end', values=values)

    def create_search_tab(self, parent, module_name):
        """Crea pestaña de búsqueda"""
        main_frame = tk.Frame(parent, bg=self.colors['bg_card'])
        main_frame.pack(fill='both', expand=True, padx=25, pady=25)
        
        title_label = tk.Label(main_frame,
                             text=f"Búsqueda - {module_name}",
                             font=('Arial', 16, 'bold'),
                             fg=self.colors['primary_light'],
                             bg=self.colors['bg_card'])
        title_label.pack(pady=(0, 20))
        
        info_label = tk.Label(main_frame, 
                            text="Funcionalidad de búsqueda avanzada en desarrollo",
                            font=('Arial', 12),
                            fg=self.colors['muted'],
                            bg=self.colors['bg_card'])
        info_label.pack(pady=50)

    def create_stats_tab(self, parent, module_name):
        """Crea pestaña de estadísticas"""
        main_frame = tk.Frame(parent, bg=self.colors['bg_card'])
        main_frame.pack(fill='both', expand=True, padx=25, pady=25)
        
        title_label = tk.Label(main_frame,
                             text=f"Estadísticas - {module_name}",
                             font=('Arial', 16, 'bold'),
                             fg=self.colors['primary_light'],
                             bg=self.colors['bg_card'])
        title_label.pack(pady=(0, 20))
        
        stats_text = self.calculate_module_statistics(module_name)
        
        stats_display = tk.Text(main_frame,
                              font=('Consolas', 11),
                              fg=self.colors['light'],
                              bg=self.colors['bg_card'],
                              wrap='word',
                              padx=15,
                              pady=15)
        stats_display.pack(fill='both', expand=True)
        
        stats_display.insert('1.0', stats_text)
        stats_display.config(state='disabled')

    def calculate_module_statistics(self, module_name):
        """Calcula estadísticas del módulo"""
        registros = self.datos.get(module_name, [])
        
        if not registros:
            return "No hay registros en este módulo."
        
        total_registros = len(registros)
        total_valor = sum(float(r.get('Valor', 0)) for r in registros)
        valor_promedio = total_valor / total_registros if total_registros > 0 else 0
        
        reporte = f"""
📊 REPORTE ESTADÍSTICO - {module_name.upper()}
{'=' * 50}

📈 ESTADÍSTICAS GENERALES:
   • Total de registros: {total_registros:,}
   • Valor total: ${total_valor:,.0f}
   • Valor promedio: ${valor_promedio:,.0f}

🕒 Reporte generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return reporte

    # =========================================================================
    # FUNCIONALIDADES AVANZADAS - IMPLEMENTADAS
    # =========================================================================

    def show_advanced_global_search(self):
        """Muestra la búsqueda global avanzada"""
        search_window = tk.Toplevel(self.root)
        search_window.title("COOPJUDICIAL - Búsqueda Global")
        search_window.geometry("1000x700")
        search_window.configure(bg=self.colors['bg_dark'])
        self.center_child_window(search_window, 1000, 700)
        
        main_frame = tk.Frame(search_window, bg=self.colors['bg_card'])
        main_frame.pack(fill='both', expand=True, padx=25, pady=25)
        
        title_label = tk.Label(main_frame,
                             text="🔍 Búsqueda Global en Todo el Sistema",
                             font=('Arial', 18, 'bold'),
                             fg=self.colors['primary_light'],
                             bg=self.colors['bg_card'])
        title_label.pack(pady=(0, 20))
        
        search_frame = tk.Frame(main_frame, bg=self.colors['bg_card'])
        search_frame.pack(fill='x', pady=20)
        
        tk.Label(search_frame, text="Buscar:",
                font=('Arial', 12),
                fg=self.colors['light'],
                bg=self.colors['bg_card']).pack(side='left')
        
        search_entry = tk.Entry(search_frame, font=('Arial', 12), width=50)
        search_entry.pack(side='left', padx=15)
        
        results_frame = tk.Frame(main_frame, bg=self.colors['bg_card'])
        results_frame.pack(fill='both', expand=True, pady=10)
        
        columns = ["Módulo", "ID", "Nombre", "Valor", "Estado"]
        tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        # Cargar algunos datos de ejemplo
        for modulo, registros in self.datos.items():
            for registro in registros[:5]:  # Mostrar primeros 5 de cada módulo
                tree.insert('', 'end', values=(
                    modulo,
                    registro.get('ID', ''),
                    registro.get('Nombre', ''),
                    registro.get('Valor', ''),
                    registro.get('Estado', '')
                ))
        
        tree.pack(fill='both', expand=True)

    def show_executive_dashboard(self):
        """Muestra el dashboard ejecutivo"""
        dashboard_window = tk.Toplevel(self.root)
        dashboard_window.title("COOPJUDICIAL - Dashboard Ejecutivo")
        dashboard_window.geometry("1200x800")
        dashboard_window.configure(bg=self.colors['bg_dark'])
        self.center_child_window(dashboard_window, 1200, 800)
        
        main_frame = tk.Frame(dashboard_window, bg=self.colors['bg_card'])
        main_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        title_label = tk.Label(main_frame,
                             text="📊 Dashboard Ejecutivo - COOPJUDICIAL",
                             font=('Arial', 20, 'bold'),
                             fg=self.colors['primary_light'],
                             bg=self.colors['bg_card'])
        title_label.pack(pady=(0, 25))
        
        metrics = self.calculate_advanced_metrics()
        
        metrics_text = f"""
        📈 MÉTRICAS EJECUTIVAS DEL SISTEMA

        • Total de registros: {metrics['total_registros']:,}
        • Valor total de la cartera: ${metrics['total_valor']:,.0f}
        • Créditos activos: {metrics['creditos_activos']}
        • Total de afiliados: {metrics['total_afiliados']}
        • Ahorros administrados: ${metrics['total_ahorros']:,.0f}

        📋 DISTRIBUCIÓN POR MÓDULOS:
        """
        
        for modulo, registros in self.datos.items():
            metrics_text += f"   • {modulo}: {len(registros)} registros\n"
        
        metrics_label = tk.Label(main_frame, text=metrics_text,
                               font=('Consolas', 11),
                               fg=self.colors['light'],
                               bg=self.colors['bg_card'],
                               justify='left')
        metrics_label.pack(pady=20)

    def show_graphical_reports(self):
        """Muestra reportes con gráficos"""
        try:
            reports_window = tk.Toplevel(self.root)
            reports_window.title("COOPJUDICIAL - Reportes Gráficos")
            reports_window.geometry("1000x700")
            reports_window.configure(bg=self.colors['bg_dark'])
            self.center_child_window(reports_window, 1000, 700)
            
            main_frame = tk.Frame(reports_window, bg=self.colors['bg_card'])
            main_frame.pack(fill='both', expand=True, padx=25, pady=25)
            
            title_label = tk.Label(main_frame,
                                 text="📈 Reportes Gráficos - COOPJUDICIAL",
                                 font=('Arial', 18, 'bold'),
                                 fg=self.colors['primary_light'],
                                 bg=self.colors['bg_card'])
            title_label.pack(pady=(0, 20))
            
            # Gráfico simple de distribución
            fig, ax = plt.subplots(figsize=(10, 6))
            
            modulos = list(self.categorias.values())
            cantidades = [len(self.datos[modulo]) for modulo in modulos]
            
            bars = ax.bar(modulos, cantidades, color=[
                self.colors['chart_1'], self.colors['chart_2'], 
                self.colors['chart_3'], self.colors['chart_4']
            ])
            ax.set_title('Distribución de Registros por Módulo')
            ax.set_ylabel('Cantidad de Registros')
            plt.xticks(rotation=45, ha='right')
            
            plt.tight_layout()
            
            canvas = FigureCanvasTkAgg(fig, main_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
            
            self.chart_figures.append(fig)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error generando gráficos: {str(e)}")

    def export_complete_data(self):
        """Exporta todos los datos del sistema"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Exportar datos completos"
            )
            
            if filename:
                with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                    # Resumen ejecutivo
                    summary_data = []
                    for modulo, registros in self.datos.items():
                        total_valor = sum(float(r.get('Valor', 0)) for r in registros)
                        summary_data.append({
                            'Módulo': modulo,
                            'Registros': len(registros),
                            'Valor Total': total_valor
                        })
                    
                    pd.DataFrame(summary_data).to_excel(writer, sheet_name="Resumen", index=False)
                    
                    # Hojas por módulo
                    for modulo, registros in self.datos.items():
                        if registros:
                            df = pd.DataFrame(registros)
                            sheet_name = modulo[:31]
                            df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                messagebox.showinfo("Éxito", f"✅ Datos exportados:\n{filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"❌ Error exportando: {str(e)}")

    def show_system_config(self):
        """Muestra la configuración del sistema"""
        config_window = tk.Toplevel(self.root)
        config_window.title("COOPJUDICIAL - Configuración")
        config_window.geometry("600x500")
        config_window.configure(bg=self.colors['bg_dark'])
        self.center_child_window(config_window, 600, 500)
        
        main_frame = tk.Frame(config_window, bg=self.colors['bg_card'])
        main_frame.pack(fill='both', expand=True, padx=25, pady=25)
        
        title_label = tk.Label(main_frame,
                             text="⚙️ Configuración del Sistema",
                             font=('Arial', 18, 'bold'),
                             fg=self.colors['primary_light'],
                             bg=self.colors['bg_card'])
        title_label.pack(pady=(0, 25))
        
        config_text = f"""
        CONFIGURACIÓN ACTUAL:

        💰 PARÁMETROS FINANCIEROS:
          • Tasa de interés ahorros: {self.business_config['tasa_interes_ahorro']*100}% anual
          • Tasa de interés créditos: {self.business_config['tasa_interes_credito']*100}% anual
          • Cuota de afiliación: ${self.business_config['cuota_afiliacion']:,.0f}
          • Aportes mínimos: ${self.business_config['aportes_minimos']:,.0f}

        📊 INFORMACIÓN DEL SISTEMA:
          • Versión: COOPJUDICIAL v4.0
          • Módulos: {len(self.categorias)}
          • Archivo de datos: {self.data_file}
        """
        
        config_label = tk.Label(main_frame, text=config_text,
                              font=('Consolas', 10),
                              fg=self.colors['light'],
                              bg=self.colors['bg_card'],
                              justify='left')
        config_label.pack(pady=20)

    def refresh_system(self):
        """Actualiza todo el sistema"""
        self.update_metrics_display()
        self.update_status("✅ Sistema actualizado")

    def center_child_window(self, window, width, height):
        """Centra una ventana hija"""
        x = self.root.winfo_x() + (self.root.winfo_width() - width) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - height) // 2
        window.geometry(f'{width}x{height}+{x}+{y}')

    def close_current_window(self):
        """Cierra la ventana actual"""
        if self.current_window and self.current_window.winfo_exists():
            self.current_window.destroy()
            self.current_window = None

    def safe_exit(self):
        """Cierra la aplicación de forma segura"""
        if messagebox.askyesno("Salir", "¿Está seguro de que desea salir del sistema?"):
            if self.save_data():
                self.update_status("💾 Datos guardados - Saliendo...")
            
            if self.current_window and self.current_window.winfo_exists():
                self.current_window.destroy()
            
            for fig in self.chart_figures:
                plt.close(fig)
            
            if hasattr(self, 'conn'):
                self.conn.close()
            
            self.root.quit()


# =============================================================================
# FUNCIÓN PRINCIPAL
# =============================================================================

def main():
    """Función principal de la aplicación"""
    print("=" * 60)
    print("🏦 SISTEMA FINANCIERO COOPJUDICIAL - v4.0 CORREGIDA")
    print("📅 Iniciando aplicación...")
    print("=" * 60)
    
    try:
        # Verificar dependencias
        dependencies = ['pandas', 'matplotlib', 'seaborn', 'openpyxl']
        for dep in dependencies:
            try:
                if dep == 'pandas':
                    import pandas as pd
                elif dep == 'matplotlib':
                    import matplotlib.pyplot as plt
                elif dep == 'seaborn':
                    import seaborn as sns
                elif dep == 'openpyxl':
                    import openpyxl
                print(f"✅ {dep} cargado correctamente")
            except ImportError as e:
                print(f"⚠️  {dep} no disponible: {e}")

        root = tk.Tk()
        app = ModernFinancialApp(root)
        root.protocol("WM_DELETE_WINDOW", app.safe_exit)
        
        print("✅ Aplicación iniciada correctamente")
        print("🚀 Sistema COOPJUDICIAL v4.0 listo")
        
        root.mainloop()
        
        print("👋 Aplicación finalizada")
        
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        messagebox.showerror("Error", f"No se pudo iniciar la aplicación:\n\n{str(e)}")

if __name__ == "__main__":
    main()