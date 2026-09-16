import psycopg2
from psycopg2 import OperationalError

def obtener_conexion():
    try:
        conexion = psycopg2.connect(
            host='localhost',
            database='CLINICA',
            user='', #usuario
            password=''  # Reemplaza con tu contraseña de pgAdmin
        )
        print("Conexión exitosa a la base de datos PostgreSQL")
        return conexion
    except OperationalError as e:
        print("Error al conectar a PostgreSQL:", e)
        return None