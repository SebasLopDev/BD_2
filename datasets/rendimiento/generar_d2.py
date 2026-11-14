
import csv
import random
from pathlib import Path

# Semilla para reproducir los mismos datos
random.seed(42)

# Cantidades de registros
cantidades = [100_000, 500_000, 1_000_000]

# Carpeta donde guardaremos los CSV
carpeta_salida = Path(__file__).resolve().parent / "datos_d2"

# Crear la carpeta si no existe
carpeta_salida.mkdir(parents=True, exist_ok=True)

# Recorrer cada cantidad de registros
for cantidad in cantidades:

    # Construir el nombre del archivo
    if cantidad == 1_000_000:
        nombre_archivo = "d2_1m.csv"
    else:
        nombre_archivo = f"d2_{cantidad // 1000}k.csv"

    # Ruta completa del archivo
    ruta_archivo = carpeta_salida / nombre_archivo

    # Generar claves aleatorias sin repetir
    numeros = random.sample(range(1, cantidad * 10 + 1), cantidad)

    # Abrir o crear el CSV
    with open(ruta_archivo, "w", newline="", encoding="utf-8") as archivo:

        # Crear escritor CSV
        escritor = csv.writer(archivo)

        # Escribir encabezados
        escritor.writerow(["clave", "nombre"])

        # Escribir los registros
        for i in range(cantidad):

            clave = numeros[i]
            nombre = "Persona_" + str(i + 1)

            escritor.writerow([clave, nombre])

    print(f"Generado: {nombre_archivo} ({cantidad} registros)")

print("Todos los datasets D2 fueron generados correctamente.")
