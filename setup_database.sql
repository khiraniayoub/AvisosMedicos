-- Script para crear la base de datos y tabla de avisos
-- Ejecutar este script después de instalar PostgreSQL

-- Crear la base de datos (si no existe)
CREATE DATABASE avisos_db;

-- Conectar a la base de datos
\c avisos_db

-- Crear la tabla de avisos
CREATE TABLE IF NOT EXISTS avisos (
    id SERIAL PRIMARY KEY,
    emisor VARCHAR(255),
    hora_solicitud VARCHAR(50),
    fecha VARCHAR(50),
    hotel VARCHAR(255),
    habitacion VARCHAR(50),
    estado VARCHAR(50),
    paciente VARCHAR(255),
    edad VARCHAR(50),
    historia_medica TEXT,
    nacionalidad VARCHAR(100),
    motivo_urgencia TEXT,
    pagador VARCHAR(100),
    seguro VARCHAR(100),
    touroperador VARCHAR(100),
    hora_aviso VARCHAR(50),
    hora_finalizacion VARCHAR(50),
    medico VARCHAR(255),
    diagnostico TEXT,
    traslado VARCHAR(50),
    tipo_traslado VARCHAR(100),
    hora_ambulancia VARCHAR(50),
    ingreso VARCHAR(50),
    medico_ingreso VARCHAR(255),
    observaciones TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crear índices para mejorar el rendimiento
CREATE INDEX IF NOT EXISTS idx_avisos_fecha ON avisos(fecha);
CREATE INDEX IF NOT EXISTS idx_avisos_estado ON avisos(estado);
CREATE INDEX IF NOT EXISTS idx_avisos_hotel ON avisos(hotel);

-- Mensaje de confirmación
SELECT 'Base de datos y tabla creadas exitosamente!' AS mensaje;
