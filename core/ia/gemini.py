import time
from dotenv import load_dotenv  # <-- Asegurar importación
from google import genai
from google.genai import types
from google.genai.errors import ServerError, APIError

from core.prompts.academico import (
    PROMPT_APUNTES_GENERAL,
    buscar_prompt_existente_db,
    guardar_nueva_materia_db,
    _obtener_prompt_generico_db
)

# Cargar variables del entorno (.env)
load_dotenv()


def generar_prompt_para_nueva_materia(client, nombre_materia):
    meta_prompt = f"""
Eres un diseñador de arquitecturas de toma de notas académicas.
El usuario va a tomar apuntes sobre la materia/área: "{nombre_materia}".

Genera una lista breve de instrucciones (de 5 a 8 puntos) sobre qué elementos específicos
debe estructurar y priorizar un asistente al procesar clases de esta materia.

Ejemplo de estructura esperada:
La materia es {nombre_materia}.
Organiza especialmente:
- Conceptos y definiciones clave.
- [Aspecto técnico 1 de la materia]
- [Aspecto técnico 2 de la materia]
- Ejemplos explicados por el profesor.
- Fórmulas, algoritmos o código si aparecen.

Responde ÚNICAMENTE con la lista de instrucciones, sin introducciones ni saludos.
"""
    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=meta_prompt
        )
        prompt_generado = response.text.strip()
        
        # Guardar en PostgreSQL
        guardar_nueva_materia_db(nombre_materia, prompt_generado)
        
        return prompt_generado
    except Exception as e:
        print(f"[Error al generar prompt dinámico]: {e}")
        return _obtener_prompt_generico_db()


def obtener_o_crear_prompt_materia(client, nombre_materia):
    prompt = buscar_prompt_existente_db(nombre_materia)
    if prompt:
        return prompt

    print(f"\n[Sistema]: Materia nueva ('{nombre_materia}'). Generando instrucciones y guardando en PostgreSQL...")
    return generar_prompt_para_nueva_materia(client, nombre_materia)


def procesar_con_gemini(
    transcripcion_raw,
    nombre_carpeta,
    num_clase,
    nombre_materia,
    retries=4,
    delay=5
):
    if not transcripcion_raw or not transcripcion_raw.strip():
        return "No se capturó audio suficiente para generar un apunte."

    # Aseguramos que tome la API Key del entorno
    client = genai.Client()
    
    prompt_materia = obtener_o_crear_prompt_materia(client, nombre_materia)

    prompt = f"""
INFORMACIÓN DE LA CLASE:
Materia: {nombre_materia}
Carpeta: {nombre_carpeta}
Número de clase: {num_clase}

INSTRUCCIONES ESPECÍFICAS DE LA MATERIA:
{prompt_materia}

TRANSCRIPCIÓN:
{transcripcion_raw}
"""

    for intento in range(1, retries + 1):
        try:
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=PROMPT_APUNTES_GENERAL,
                    temperature=0.4
                )
            )
            return response.text

        except (ServerError, APIError) as e:
            print(f"\n[Error API] Código: {getattr(e, 'code', 'Desconocido')} - Intento {intento}/{retries}.")
            if intento < retries:
                time.sleep(delay)
            else:
                raise e