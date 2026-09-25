import os
from dotenv import load_dotenv, set_key

ENV_PATH = ".env"

def obtener_api_key():
    """Verifica si existe una API Key válida."""
    load_dotenv(ENV_PATH)
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key.strip() == "TU_API_KEY_AQUI" or api_key.strip() == "":
        return None
    return api_key

def guardar_api_key(nueva_key):
    """Guarda la nueva API Key en el archivo .env y en el entorno actual."""
    if not os.path.exists(ENV_PATH):
        with open(ENV_PATH, "w") as f:
            f.write("")

    set_key(ENV_PATH, "GEMINI_API_KEY", nueva_key)
    os.environ["GEMINI_API_KEY"] = nueva_key
    return True