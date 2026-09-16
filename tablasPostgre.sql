-- SQLINES DEMO *** ========================================
-- 1.... SQLINES DEMO ***
-- SQLINES DEMO *** ========================================

-- SQLINES FOR EVALUATION USE ONLY
CREATE TABLE historial_medico (
    id_historial_medico INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    antecedentes_historial VARCHAR(100),
    alergias_historial VARCHAR(100),
    enfermedades_cronicas VARCHAR(100)
);

CREATE TABLE medico (
    id_medico INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    nombre VARCHAR(50) NOT NULL,
    apellido VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    estado VARCHAR(10) CHECK(estado IN ('activo','inactivo')) NOT NULL
);

CREATE TABLE medicamento (
    id_medicamento INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    nombre_medcmnto VARCHAR(100) NOT NULL,
    presentacion VARCHAR(20) CHECK (presentacion IN ('CAPSULA','JARABE','INYECTABLE','MASTICABLE')),
    descrip_medcmnto VARCHAR(200)
);

CREATE TABLE enfermedad (
    id_enfermedad INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    nombre_enfrmdad VARCHAR(100) NOT NULL,
    descrip_enfrmdad VARCHAR(255)
);

CREATE TABLE especialidad (
    id_especialidad INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    nombre_espclidad VARCHAR(100) NOT NULL,
    descripcion_espclidad VARCHAR(200)    
);

CREATE TABLE rol (
    id_rol INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    nombre_rol VARCHAR(25) CHECK(nombre_rol IN ('PACIENTE','MEDICO','ADMIN')) NOT NULL
);

CREATE TABLE sala (
    id_sala INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    nombre VARCHAR(50) NOT NULL,
    tipo VARCHAR(50),
    estado VARCHAR(20) CHECK (estado IN ('disponible','ocupado','no-disponible')) NOT NULL
);

-- SQLINES DEMO *** ========================================
-- SQLINES DEMO *** RIAS
-- SQLINES DEMO *** ========================================

CREATE TABLE paciente (
    id_paciente INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    nombre VARCHAR(50) NOT NULL,
    apellido VARCHAR(50) NOT NULL,
    dni VARCHAR(15) UNIQUE NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    sexo CHAR(1) CHECK (sexo IN ('M', 'F')) NOT NULL,
    telefono VARCHAR(20),
    direccion VARCHAR(200),
    email VARCHAR(100) UNIQUE NOT NULL,
    id_historial_medico INT,
    FOREIGN KEY(id_historial_medico) REFERENCES historial_medico(id_historial_medico)
);

CREATE TABLE receta_medicamento (
    id_receta_medicamento INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    indicaciones_medcmnto VARCHAR(255),    
    id_medicamento INT NOT NULL,
    FOREIGN KEY(id_medicamento) REFERENCES medicamento(id_medicamento)
);

CREATE TABLE usuario_sistema (
    id_usuario INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    nombre_user VARCHAR(50) NOT NULL,
    contrasena_user VARCHAR(100),
    email_user VARCHAR(100) UNIQUE,
    id_rol INT NOT NULL,
    id_paciente INT NULL,
    id_medico INT NULL,
    FOREIGN KEY(id_rol) REFERENCES rol(id_rol),
    FOREIGN KEY(id_paciente) REFERENCES paciente(id_paciente),
    FOREIGN KEY(id_medico) REFERENCES medico(id_medico)
);

CREATE TABLE turno_medico (
    id_turno INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    dia_semana VARCHAR(20) NOT NULL,
    hora_inicio VARCHAR(10) NOT NULL,
    hora_fin VARCHAR(10) NOT NULL,
    id_medico INT NOT NULL,
    FOREIGN KEY(id_medico) REFERENCES medico(id_medico)
);

-- SQLINES DEMO *** ========================================
-- SQLINES DEMO *** TAS Y FLUJOS
-- SQLINES DEMO *** ========================================

CREATE TABLE cita (
    id_cita INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    fecha DATE NOT NULL,
    hora VARCHAR(10) NOT NULL,
    estado VARCHAR(20) CHECK (estado IN ('disponible','ocupado','no_disponible')) NOT NULL,
    motivo VARCHAR(255) NOT NULL,
    id_medico INT NOT NULL,
    id_paciente INT NOT NULL,
    id_sala INT,
    FOREIGN KEY(id_medico) REFERENCES medico(id_medico),
    FOREIGN KEY(id_paciente) REFERENCES paciente(id_paciente),
    FOREIGN KEY(id_sala) REFERENCES sala(id_sala)
);

CREATE TABLE examen_medico (
    id_examen INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    tipo_exmen VARCHAR(20) CHECK (tipo_exmen IN ('SANGRE','RAYOSX','ECOGRAFIA','ORINA')) NOT NULL, 
    fecha_exmen DATE NOT NULL,
    resultado_exmen VARCHAR(180) NOT NULL,
    id_cita INT NOT NULL,
    FOREIGN KEY(id_cita) REFERENCES cita(id_cita)
);

CREATE TABLE receta (
    id_receta INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    indicaciones_receta VARCHAR(255) NOT NULL,
    id_cita INT NOT NULL,
    FOREIGN KEY(id_cita) REFERENCES cita(id_cita)
);

CREATE TABLE diagnostico (
    id_diagnostico INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    descripcion_dgnstico VARCHAR(255),
    id_enfermedad INT NOT NULL,
    id_cita INT NOT NULL,
    FOREIGN KEY(id_enfermedad) REFERENCES enfermedad(id_enfermedad),
    FOREIGN KEY(id_cita) REFERENCES cita(id_cita)
);

CREATE TABLE tratamiento (
    id_tratamiento INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    descrip_trtmnto VARCHAR(255),
    duracion_trtmnto INT,
    id_diagnostico INT NOT NULL,
    FOREIGN KEY(id_diagnostico) REFERENCES diagnostico(id_diagnostico)
);

CREATE TABLE factura (
    id_factura INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    monto_total DECIMAL(10,2) NOT NULL,
    estado VARCHAR(25) CHECK (estado IN ('CANCELADO', 'PAGADO', 'PENDIENTE')),
    metodo_facturacion VARCHAR(100),
    id_usuario INT NOT NULL,
    id_paciente INT NOT NULL,
    CONSTRAINT fk_factura_usuario FOREIGN KEY (id_usuario) REFERENCES usuario_sistema(id_usuario),
    CONSTRAINT fk_factura_paciente FOREIGN KEY (id_paciente) REFERENCES paciente(id_paciente)
);

CREATE TABLE pago (
    id_pago INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    monto DECIMAL(10,2) NOT NULL,
    metodo_pago VARCHAR(25) CHECK(metodo_pago IN ('EFECTIVO','TARJETA')) NOT NULL,
    fecha_pago DATE NOT NULL,
    id_cita INT NOT NULL,
    FOREIGN KEY(id_cita) REFERENCES cita(id_cita)
);
