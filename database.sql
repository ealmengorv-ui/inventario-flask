CREATE DATABASE inventario_db;

CREATE TABLE productos (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(120) NOT NULL,
    categoria VARCHAR(80) NOT NULL,
    precio NUMERIC(10,2) NOT NULL CHECK (precio > 0),
    existencia INTEGER NOT NULL CHECK (existencia >= 0),
    activo BOOLEAN NOT NULL DEFAULT TRUE
);

INSERT INTO productos
(codigo, nombre, categoria, precio, existencia, activo)
VALUES
('TEC001', 'Mouse inalambrico', 'Accesorios', 125.50, 15, TRUE),
('TEC002', 'Teclado mecanico', 'Accesorios', 350.00, 10, TRUE),
('TEC003', 'Monitor 24 pulgadas', 'Monitores', 1450.00, 8, TRUE),
('TEC004', 'Laptop Core i5', 'Computadoras', 5200.00, 5, TRUE),
('TEC005', 'Memoria USB 64GB', 'Almacenamiento', 95.00, 25, TRUE);