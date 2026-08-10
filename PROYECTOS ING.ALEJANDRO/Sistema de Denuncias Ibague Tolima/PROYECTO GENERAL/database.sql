-- Crear base de datos
CREATE DATABASE sistema_app;
\c sistema_app;

-- Tabla de usuarios
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    rol VARCHAR(20) DEFAULT 'usuario',
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de productos (inventario)
CREATE TABLE productos (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    categoria VARCHAR(50),
    precio_compra DECIMAL(10,2),
    precio_venta DECIMAL(10,2),
    stock_actual INTEGER DEFAULT 0,
    stock_minimo INTEGER DEFAULT 5,
    unidad_medida VARCHAR(20),
    ubicacion VARCHAR(100),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de movimientos de inventario
CREATE TABLE movimientos (
    id SERIAL PRIMARY KEY,
    producto_id INTEGER REFERENCES productos(id),
    tipo_movimiento VARCHAR(20) CHECK (tipo_movimiento IN ('entrada', 'salida', 'ajuste')),
    cantidad INTEGER NOT NULL,
    stock_anterior INTEGER,
    stock_nuevo INTEGER,
    motivo TEXT,
    usuario_id INTEGER REFERENCES usuarios(id),
    fecha_movimiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de denuncias
CREATE TABLE denuncias (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    contenido TEXT NOT NULL,
    categoria VARCHAR(50),
    ubicacion VARCHAR(200),
    evidencia_url VARCHAR(500),
    estado VARCHAR(20) DEFAULT 'pendiente',
    usuario_id INTEGER REFERENCES usuarios(id),
    fecha_denuncia TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_resolucion TIMESTAMP,
    resolucion TEXT
);

-- Tabla de comentarios en denuncias
CREATE TABLE comentarios_denuncias (
    id SERIAL PRIMARY KEY,
    denuncia_id INTEGER REFERENCES denuncias(id) ON DELETE CASCADE,
    usuario_id INTEGER REFERENCES usuarios(id),
    comentario TEXT NOT NULL,
    fecha_comentario TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertar usuario administrador
INSERT INTO usuarios (username, password, email, rol) 
VALUES ('admin', 'admin123', 'admin@sistema.com', 'admin');

-- Insertar productos de ejemplo
INSERT INTO productos (codigo, nombre, descripcion, categoria, precio_compra, precio_venta, stock_actual, stock_minimo, unidad_medida) VALUES
('PROD-001', 'Laptop HP', 'Laptop HP 15.6 pulgadas', 'Electrónica', 450000, 650000, 10, 3, 'unidad'),
('PROD-002', 'Mouse Logitech', 'Mouse inalámbrico', 'Periféricos', 25000, 45000, 25, 5, 'unidad'),
('PROD-003', 'Teclado Mecánico', 'Teclado RGB mecánico', 'Periféricos', 80000, 120000, 8, 2, 'unidad'),
('PROD-004', 'Monitor 24"', 'Monitor LED Full HD', 'Electrónica', 280000, 380000, 5, 2, 'unidad');