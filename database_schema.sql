-- Estructura de Base de Datos para Astor Simulador
-- Este archivo sirve para recrear las tablas en tu servidor MySQL

CREATE DATABASE IF NOT EXISTS astor_simulador;
USE astor_simulador;

-- 1. Clientes (Centraliza información de contacto)
CREATE TABLE IF NOT EXISTS clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    telefono VARCHAR(20),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX (email)
) ENGINE=InnoDB;

-- 2. Registro Maestro de Simulaciones
CREATE TABLE IF NOT EXISTS simulaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    tipo ENUM('PROYECTO_5', 'PROYECTO_COSTOS') NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 3. Parámetros de Proyecto 5%
CREATE TABLE IF NOT EXISTS sim_proyecto_5 (
    simulacion_id INT PRIMARY KEY,
    monto_mensual DECIMAL(15,2) NOT NULL,
    edad_actual TINYINT NOT NULL,
    tasa_anual_estimada DECIMAL(5,2) DEFAULT 10.00,
    FOREIGN KEY (simulacion_id) REFERENCES simulaciones(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 4. Parámetros de Proyecto Costos
CREATE TABLE IF NOT EXISTS sim_proyecto_costos (
    simulacion_id INT PRIMARY KEY,
    renta_deseada DECIMAL(15,2) NOT NULL,
    edad_actual TINYINT NOT NULL,
    edad_retiro TINYINT NOT NULL,
    patrimonio_actual DECIMAL(15,2) DEFAULT 0.00,
    FOREIGN KEY (simulacion_id) REFERENCES simulaciones(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 5. Aportaciones Extra (Solo para Proyecto 5%)
CREATE TABLE IF NOT EXISTS aportaciones_extra (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sim_p5_id INT NOT NULL,
    anio_relativo TINYINT NOT NULL,
    mes_relativo TINYINT NOT NULL,
    monto DECIMAL(15,2) NOT NULL,
    FOREIGN KEY (sim_p5_id) REFERENCES sim_proyecto_5(simulacion_id) ON DELETE CASCADE
) ENGINE=InnoDB;
