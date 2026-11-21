-- Consultas de verificación de volumen, claves foráneas y análisis relacional
-- Semilla utilizada: 20261120

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
