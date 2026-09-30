import os
import psycopg2
from psycopg2 import OperationalError
from dotenv import load_dotenv

# Cargar las variables del archivo .env
load_dotenv()

def obtener_conexion():
    try:
        # Extraer la URL de conexión de Supabase desde el archivo .env
        url_conexion = os.getenv("DATABASE_URL")
        
        # Conectar usando la URL
        conexion = psycopg2.connect(url_conexion)
        print("Conexión exitosa a la base de datos PostgreSQL")
        return conexion
        
    except OperationalError as e:
        print("Error al conectar a PostgreSQL:", e)
        return None