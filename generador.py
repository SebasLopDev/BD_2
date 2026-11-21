import csv
import random
from datetime import date, timedelta
from pathlib import Path

# ==========================================
# PARÁMETROS REPRODUCIBLES (DOCUMENTAR)
# ==========================================
SEED = 20261120
NUM_PACIENTES = 50_000
NUM_MEDICOS = 500
NUM_SALAS = 60
NUM_CITAS = 1_000_000  # Garantiza al menos 1,000,000 de registros en cita
FECHA_INICIO_CITAS = date(2025, 1, 1)
DIAS_RANGO_CITAS = 730  # 2 años de citas
OUTPUT_DIR = Path("dataset_clinica")

NOMBRES = [
    "Carlos", "Maria", "Jose", "Ana", "Luis", "Lucia", "Jorge", "Elena",
    "Diego", "Valeria", "Andres", "Camila", "Fernando", "Sofia", "Mateo", "Paola"
]
APELLIDOS = [
    "Quispe", "Huaman", "Mamani", "Flores", "Rojas", "Gomez", "Perez", "Chavez",
    "Vargas", "Castro", "Mendoza", "Salazar", "Torres", "Reyes", "Paredes", "Castillo"
]
CALLES = [
    "Av. Ejercito", "Calle Santa Catalina", "Av. Parra", "Urb. Cayma",
    "Av. Bolognesi", "Calle Moral", "Av. Dolores", "Urb. Yanahuara"
]
TIPOS_SALA = ["Consulta Externa", "Emergencia", "Procedimientos", "Diagnostico"]
ESTADOS_SALA = ["disponible", "ocupado", "no-disponible"]
ESTADOS_CITA = ["disponible", "ocupado", "no_disponible"]
MOTIVOS_CITA = [
    "Control general", "Consulta de especialidad", "Seguimiento de tratamiento",
    "Evaluacion de resultados", "Chequeo preventivo", "Dolor agudo"
]


def fecha_nacimiento_aleatoria(rng: random.Random) -> date:
    inicio = date(1945, 1, 1)
    fin = date(2020, 12, 31)
    delta = (fin - inicio).days
    return inicio + timedelta(days=rng.randrange(delta))


def fecha_hora_cita_aleatoria(rng: random.Random) -> tuple[str, str]:
    d = FECHA_INICIO_CITAS + timedelta(days=rng.randrange(DIAS_RANGO_CITAS))
    minuto_total = rng.randrange(8 * 60, 20 * 60, 15)  # 08:00 a 19:45 cada 15 min
    hh = minuto_total // 60
    mm = minuto_total % 60
    return d.isoformat(), f"{hh:02d}:{mm:02d}"


def generar_pacientes(rng: random.Random, path: Path) -> list[int]:
    ids = []
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "id_paciente", "nombre", "apellido", "dni", "fecha_nacimiento",
            "sexo", "telefono", "direccion", "email"
        ])
        for i in range(1, NUM_PACIENTES + 1):
            nombre = rng.choice(NOMBRES)
            apellido = rng.choice(APELLIDOS)
            dni = f"{10000000 + i:08d}"
            fnac = fecha_nacimiento_aleatoria(rng).isoformat()
            sexo = "M" if i % 2 == 1 else "F"
            telefono = f"9{rng.randint(10000000, 99999999)}"
            direccion = f"{rng.choice(CALLES)} {rng.randint(100, 999)}"
            email = f"paciente.{i}.{dni}@clinica-demo.local"
            writer.writerow([i, nombre, apellido, dni, fnac, sexo, telefono, direccion, email])
            ids.append(i)
    return ids


def generar_medicos(rng: random.Random, path: Path) -> list[int]:
    ids = []
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ID_MEDICO", "NOMBRE", "APELLIDO", "EMAIL", "ESTADO"])
        for i in range(1, NUM_MEDICOS + 1):
            nombre = rng.choice(NOMBRES)
            apellido = rng.choice(APELLIDOS)
            email = f"medico.{i}@clinica-demo.local"
            estado = "activo" if rng.random() < 0.85 else "inactivo"
            writer.writerow([i, nombre, apellido, email, estado])
            ids.append(i)
    return ids


def generar_salas(rng: random.Random, path: Path) -> list[int]:
    ids = []
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ID_SALA", "NOMBRE", "TIPO", "ESTADO"])
        for i in range(1, NUM_SALAS + 1):
            tipo = rng.choice(TIPOS_SALA)
            nombre = f"Sala {i:03d}"
            estado = rng.choice(ESTADOS_SALA)
            writer.writerow([i, nombre, tipo, estado])
            ids.append(i)
    return ids


def generar_citas(
    rng: random.Random,
    path: Path,
    ids_paciente: list[int],
    ids_medico: list[int],
    ids_sala: list[int],
) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "ID_CITA", "FECHA", "HORA", "ESTADO", "MOTIVO",
            "ID_MEDICO", "ID_PACIENTE", "ID_SALA"
        ])
        for i in range(1, NUM_CITAS + 1):
            fecha, hora = fecha_hora_cita_aleatoria(rng)
            estado = rng.choice(ESTADOS_CITA)
            motivo = rng.choice(MOTIVOS_CITA)
            id_medico = rng.choice(ids_medico)
            id_paciente = rng.choice(ids_paciente)
            id_sala = rng.choice(ids_sala)
            writer.writerow([i, fecha, hora, estado, motivo, id_medico, id_paciente, id_sala])


def verificar_integridad(
    pacientes: list[int],
    medicos: list[int],
    salas: list[int],
    cita_csv: Path,
) -> int:
    set_pac = set(pacientes)
    set_med = set(medicos)
    set_sal = set(salas)

    total_citas = 0
    ids_cita = set()
    huerfanos_pac = 0
    huerfanos_med = 0
    huerfanos_sal = 0

    with cita_csv.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_citas += 1
            cid = int(row["ID_CITA"])
            pid = int(row["ID_PACIENTE"])
            mid = int(row["ID_MEDICO"])
            sid = int(row["ID_SALA"])
            ids_cita.add(cid)
            if pid not in set_pac:
                huerfanos_pac += 1
            if mid not in set_med:
                huerfanos_med += 1
            if sid not in set_sal:
                huerfanos_sal += 1

    assert total_citas >= 1_000_000, f"Se esperaban >= 1,000,000 citas, hay {total_citas}"
    assert len(ids_cita) == total_citas, "Hay ID_CITA duplicados"
    assert huerfanos_pac == 0, f"Hay {huerfanos_pac} citas con ID_PACIENTE inválido"
    assert huerfanos_med == 0, f"Hay {huerfanos_med} citas con ID_MEDICO inválido"
    assert huerfanos_sal == 0, f"Hay {huerfanos_sal} citas con ID_SALA inválido"

    print("=== VERIFICACIÓN EXITOSA ===")
    print(f"Pacientes : {len(pacientes)}")
    print(f"Medicos   : {len(medicos)}")
    print(f"Salas     : {len(salas)}")
    print(f"Citas     : {total_citas}")
    print("Huerfanos FK (Paciente / Medico / Sala): 0 / 0 / 0")
    return total_citas


def generar_archivos_sql(output_dir: Path, total_citas: int) -> None:
    carga_sql = f"""-- Generado automáticamente con SEED={SEED}
-- Pacientes: {NUM_PACIENTES}, Medicos: {NUM_MEDICOS}, Salas: {NUM_SALAS}, Citas: {total_citas}

CREATE DATABASE IF NOT EXISTS clinica_bd2;
USE clinica_bd2;

DROP TABLE IF EXISTS Cita;
DROP TABLE IF EXISTS Sala;
DROP TABLE IF EXISTS Medico;
DROP TABLE IF EXISTS Paciente;

CREATE TABLE Paciente (
    id_paciente INT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    apellido VARCHAR(50) NOT NULL,
    dni VARCHAR(15) UNIQUE NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    sexo CHAR(1) NOT NULL CHECK (sexo IN ('M', 'F')),
    telefono VARCHAR(20),
    direccion VARCHAR(200),
    email VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE Medico (
    ID_MEDICO INT PRIMARY KEY,
    NOMBRE VARCHAR(50) NOT NULL,
    APELLIDO VARCHAR(50) NOT NULL,
    EMAIL VARCHAR(100) UNIQUE NOT NULL,
    ESTADO VARCHAR(15) NOT NULL CHECK (ESTADO IN ('activo', 'inactivo'))
);

CREATE TABLE Sala (
    ID_SALA INT PRIMARY KEY,
    NOMBRE VARCHAR(50) NOT NULL,
    TIPO VARCHAR(50),
    ESTADO VARCHAR(20) NOT NULL CHECK (ESTADO IN ('disponible', 'ocupado', 'no-disponible'))
);

CREATE TABLE Cita (
    ID_CITA BIGINT PRIMARY KEY,
    FECHA DATE NOT NULL,
    HORA VARCHAR(10) NOT NULL,
    ESTADO VARCHAR(20) NOT NULL CHECK (ESTADO IN ('disponible', 'ocupado', 'no_disponible')),
    MOTIVO VARCHAR(255) NOT NULL,
    ID_MEDICO INT NOT NULL,
    ID_PACIENTE INT NOT NULL,
    ID_SALA INT NOT NULL,
    CONSTRAINT fk_cita_medico FOREIGN KEY (ID_MEDICO) REFERENCES Medico(ID_MEDICO),
    CONSTRAINT fk_cita_paciente FOREIGN KEY (ID_PACIENTE) REFERENCES Paciente(id_paciente),
    CONSTRAINT fk_cita_sala FOREIGN KEY (ID_SALA) REFERENCES Sala(ID_SALA)
);

-- Carga de CSVs (ajustar ruta si se ejecuta desde otro directorio)
LOAD DATA LOCAL INFILE 'paciente.csv'
INTO TABLE Paciente
FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\\n'
IGNORE 1 LINES;

LOAD DATA LOCAL INFILE 'medico.csv'
INTO TABLE Medico
FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\\n'
IGNORE 1 LINES;

LOAD DATA LOCAL INFILE 'sala.csv'
INTO TABLE Sala
FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\\n'
IGNORE 1 LINES;

LOAD DATA LOCAL INFILE 'cita.csv'
INTO TABLE Cita
FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\\n'
IGNORE 1 LINES;
"""

    consultas_sql = f"""-- Consultas de verificación de volumen, claves foráneas y análisis relacional
-- Semilla utilizada: {SEED}

-- 1. Verificar conteo de registros por tabla (debe haber al menos 1,000,000 en Cita)
SELECT 'Paciente' AS tabla, COUNT(*) AS total_registros FROM Paciente
UNION ALL
SELECT 'Medico', COUNT(*) FROM Medico
UNION ALL
SELECT 'Sala', COUNT(*) FROM Sala
UNION ALL
SELECT 'Cita', COUNT(*) FROM Cita;

-- 2. Verificar integridad referencial (claves foráneas sin huérfanos: todo debe ser 0)
SELECT
    SUM(CASE WHEN p.id_paciente IS NULL THEN 1 ELSE 0 END) AS citas_sin_paciente,
    SUM(CASE WHEN m.ID_MEDICO IS NULL THEN 1 ELSE 0 END) AS citas_sin_medico,
    SUM(CASE WHEN s.ID_SALA IS NULL THEN 1 ELSE 0 END) AS citas_sin_sala
FROM Cita c
LEFT JOIN Paciente p ON c.ID_PACIENTE = p.id_paciente
LEFT JOIN Medico m ON c.ID_MEDICO = m.ID_MEDICO
LEFT JOIN Sala s ON c.ID_SALA = s.ID_SALA;

-- 3. Distribución de citas por estado
SELECT ESTADO, COUNT(*) AS total_citas
FROM Cita
GROUP BY ESTADO
ORDER BY total_citas DESC;

-- 4. Top 10 médicos con mayor cantidad de citas
SELECT
    m.ID_MEDICO,
    CONCAT(m.NOMBRE, ' ', m.APELLIDO) AS medico,
    m.ESTADO,
    COUNT(c.ID_CITA) AS total_citas
FROM Medico m
JOIN Cita c ON m.ID_MEDICO = c.ID_MEDICO
GROUP BY m.ID_MEDICO, m.NOMBRE, m.APELLIDO, m.ESTADO
ORDER BY total_citas DESC
LIMIT 10;

-- 5. Cantidad de citas por tipo de sala
SELECT
    s.TIPO,
    COUNT(c.ID_CITA) AS total_citas
FROM Sala s
LEFT JOIN Cita c ON s.ID_SALA = c.ID_SALA
GROUP BY s.TIPO
ORDER BY total_citas DESC;

-- 6. Detalle de muestra con JOIN entre las 4 tablas
SELECT
    c.ID_CITA,
    c.FECHA,
    c.HORA,
    c.ESTADO AS estado_cita,
    c.MOTIVO,
    CONCAT(p.nombre, ' ', p.apellido) AS paciente,
    CONCAT(m.NOMBRE, ' ', m.APELLIDO) AS medico,
    s.NOMBRE AS sala
FROM Cita c
JOIN Paciente p ON c.ID_PACIENTE = p.id_paciente
JOIN Medico m ON c.ID_MEDICO = m.ID_MEDICO
JOIN Sala s ON c.ID_SALA = s.ID_SALA
LIMIT 20;
"""

    (output_dir / "01_schema_y_carga.sql").write_text(carga_sql, encoding="utf-8")
    (output_dir / "02_consultas_y_verificacion.sql").write_text(consultas_sql, encoding="utf-8")
    print("Archivos SQL generados: 01_schema_y_carga.sql y 02_consultas_y_verificacion.sql")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rng = random.Random(SEED)

    pac_path = OUTPUT_DIR / "paciente.csv"
    med_path = OUTPUT_DIR / "medico.csv"
    sal_path = OUTPUT_DIR / "sala.csv"
    cit_path = OUTPUT_DIR / "cita.csv"

    pacientes = generar_pacientes(rng, pac_path)
    medicos = generar_medicos(rng, med_path)
    salas = generar_salas(rng, sal_path)
    generar_citas(rng, cit_path, pacientes, medicos, salas)
    total_citas = verificar_integridad(pacientes, medicos, salas, cit_path)
    generar_archivos_sql(OUTPUT_DIR, total_citas)


if __name__ == "__main__":
    main()
