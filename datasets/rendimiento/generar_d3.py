
import csv
import random
from pathlib import Path

# Semilla para reproducir las mismas consultas
random.seed(42)

# Carpetas de entrada y salida
carpeta_base = Path(__file__).resolve().parent
carpeta_entrada = carpeta_base / "datos_d2"
carpeta_salida = carpeta_base / "datos_d3"

# Crear carpeta de salida
carpeta_salida.mkdir(parents=True, exist_ok=True)

# Configuración de las consultas
cantidades = [100_000, 500_000, 1_000_000]
cantidad_consultas = 10_000
s = 1.0

# Procesar cada dataset D2
for cantidad in cantidades:

    # Construir nombres de archivos
    if cantidad == 1_000_000:
        nombre_entrada = "d2_1m.csv"
        nombre_salida = "d3_1m.csv"
    else:
        nombre_entrada = f"d2_{cantidad // 1000}k.csv"
        nombre_salida = f"d3_{cantidad // 1000}k.csv"

    ruta_entrada = carpeta_entrada / nombre_entrada
    ruta_salida = carpeta_salida / nombre_salida

    # Leer las claves de D2
    claves = []

    with open(ruta_entrada, "r", newline="", encoding="utf-8") as archivo:
        lector = csv.DictReader(archivo)

        for fila in lector:
            clave = int(fila["clave"])
            claves.append(clave)

    # Calcular los pesos de Zipf
    pesos = [
        1 / (i ** s)
        for i in range(1, len(claves) + 1)
    ]

    # Generar las consultas
    consultas = random.choices(
        claves,
        weights=pesos,
        k=cantidad_consultas
    )

    # Guardar las consultas en CSV
    with open(ruta_salida, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)

        escritor.writerow(["clave"])

        for clave in consultas:
            escritor.writerow([clave])

    print(f"Generado: {nombre_salida} ({cantidad_consultas} consultas)")

print("Todos los datasets D3 fueron generados correctamente.")
