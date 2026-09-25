import sys
import os
import re
import psycopg
from datetime import datetime
from google import genai
from dotenv import load_dotenv

from voice.texto_voz import SpeechToText
from voice.voz_texto import hablar
from tareas.modulo_deteccion import preprocesar_entrada

load_dotenv()

stt = SpeechToText()
client = genai.Client()

PATRON_LIMPIEZA = re.compile(
    r"^.*?(\banota\b|\bguarda\b|\btoma nota de\b|\bhaz una nota de\b|\bapunta\b)\s*(que|una nota que diga|esta nota|nota)?\s*",
    re.IGNORECASE
)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from base_datos.conexion import obtener_conexion


def extraer_contenido_nota(texto: str) -> str:
    """Limpia muletillas de voz en una sola pasada."""
    texto_limpio = PATRON_LIMPIEZA.sub("", texto).strip()
    return texto_limpio if texto_limpio else texto


def formatear_nota_con_gemini(texto_raw: str) -> str:
    """Envía la transcripción a Gemini usando el cliente ya instanciado."""
    # Si la nota es muy corta (ej. "comprar leche"), no vale la pena llamar a la API
    if len(texto_raw.split()) <= 2:
        return texto_raw

    try:
        prompt = (
            f"Transforma la nota de voz: '{texto_raw}'. "
            f"Reglas: Pásala a 2da persona (ej. 'tengo' -> 'tienes'), corrige ortografía, "
            f"sé ultra breve, sin saludos ni introducciones."
        )
        
        response = client.models.generate_content(
            model='gemini-1.5-flash', # gemini-1.5-flash es más rápido y tiene menor latencia de respuesta
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        print(f"[Error Gemini Nota]: {e}")
        return texto_raw


def guardar_nota_bd(usuario_id: int, contenido: str) -> bool:
    """Inserta en la BD usando la conexión modular."""
    try:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO public.bitacora_notas (usuario_id, tipo, contenido, etiquetas)
                    VALUES (%s, 'nota_rapida', %s, ARRAY['temporal_24h']);
                """, (usuario_id, contenido))
                conn.commit()
        return True
    except Exception as e:
        print(f"[Error BD Nota]: {e}")
        return False


def escuchar_nota(usuario_id: int = 1):
    texto = stt.listen()

    if not texto:
        hablar("No te escuché")
        return None

    # 3. OPTIMIZACIÓN: Se elimina hablar("Procesando...") que congelaba la ejecución
    print(f"🎙️ [Escuchado]: {texto}")
    
    # Procesamiento rápido en memoria + API
    contenido_bruto = extraer_contenido_nota(texto)
    nota_final = formatear_nota_con_gemini(contenido_bruto)
    
    print(f"📝 [Nota Procesada]: {nota_final}")
    
    # Guardado directo
    exito = guardar_nota_bd(usuario_id, nota_final)
    
    # ÚNICO AUDIO: Una sola confirmación fluida al terminar
    if exito:
        hablar(f"Anotado. {nota_final}")
    else:
        hablar("No pude guardar la nota.")
        
    return nota_final