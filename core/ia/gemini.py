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
Eres un diseñador experto en arquitecturas de toma de notas e instruccionales.
El usuario procesará una clase de la materia/área: "{nombre_materia}".

Analiza la naturaleza de "{nombre_materia}" e identifica los 5 a 8 elementos críticos indispensables que el asistente debe priorizar al tomar notas de esta materia en específico. 

Reglas de adaptación:
- Si es una materia práctica o de código/sistemas: prioriza arquitecturas, comandos, código, librerías y lógica de implementación.
- Si es una materia matemática o de modelado: prioriza notación formal, variables, derivaciones, teoremas, fórmulas y casos de borde.
- Si es una materia conceptual o teórica: prioriza definiciones, analogías, modelos mentales, taxonomías y comparativas.

Genera la respuesta adaptada con el siguiente formato estricto:

La materia es {nombre_materia}.
Organiza especialmente:
- **[Elemento clave adaptado 1]:** [Descripción breve de qué extraer exactamente en esta materia].
- **[Elemento clave adaptado 2]:** [Descripción breve de qué extraer exactamente en esta materia].
- **[Elemento clave adaptado 3]:** [Descripción breve de qué extraer exactamente en esta materia].
- **[Elemento clave adaptado 4]:** [Descripción breve de qué extraer exactamente en esta materia].
- **[Elemento clave adaptado 5]:** [Descripción breve de qué extraer exactamente en esta materia].
- **[Elemento clave adaptado 6 (opcional)]:** [Descripción breve].

Responde ÚNICAMENTE con la lista de instrucciones, sin introducciones, explicaciones previas ni saludos.
"""
    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
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
                model="gemini-3.6-flash",
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