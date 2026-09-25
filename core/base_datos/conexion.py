import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

def obtener_conexion():
    """
    Crea y devuelve la conexion con la base 
    """

    return psycopg.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

if __name__ == "__main__":
    try:
        conexion = obtener_conexion()
        print("Conexión exitosa con PostgreSQL")
        conexion.close()
    except Exception as e:
        print(f"Error de conexión: {e}")

