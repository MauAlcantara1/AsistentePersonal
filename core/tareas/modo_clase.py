import os
import re
import sys
import time
import threading
from datetime import datetime
from google import genai
from google.genai.errors import ServerError, APIError
from dotenv import load_dotenv
from core.voice.texto_voz import SpeechToText
from core.configuracion.archivo_configuracion import configurar_boveda
from core.configuracion.archivo_configuracion import cargar_configuracion
from core.ia.gemini import procesar_con_gemini
from core.tareas.modo_exposicion import inicio
import json
config = cargar_configuracion()

RUTA_BOVEDA = config["ruta_boveda"]
RUTA_NOTAS = os.path.join(RUTA_BOVEDA)
ARCHIVO_TEMP = "temp_transcripcion.txt"
ARCHIVO_TEMP_JSON = "temp_clase.json"
load_dotenv()  
grabando = True
pausado = False
regresar_menu = False
stt = SpeechToText()


def crear_carpeta_fisica(nombre):
    """Crea la carpeta en la bóveda si no existe."""
    if not nombre or not nombre.strip():
        return False, "El nombre no puede estar vacío"
    ruta_nueva = os.path.join(RUTA_NOTAS, nombre.strip())
    if os.path.exists(ruta_nueva):
        return False, "Esa carpeta ya existe"
    try:
        os.mkdir(ruta_nueva)
        return True, f"Carpeta '{nombre}' creada con éxito"
    except Exception as e:
        return False, f"Error al crear la carpeta: {str(e)}"

def obtener_siguiente_nombre_clase(ruta_carpeta):
    archivos = os.listdir(ruta_carpeta)
    numeros_clases = []
    patron = re.compile(r"^(\d+)Clase-", re.IGNORECASE)
    
    for archivo in archivos:
        coincidencia = patron.match(archivo)
        if coincidencia:
            numeros_clases.append(int(coincidencia.group(1)))
            
    siguiente_numero = max(numeros_clases) + 1 if numeros_clases else 1
    
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", 
             "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    ahora = datetime.now()
    fecha_str = f"{ahora.day}-{meses[ahora.month - 1]}-{ahora.year}"
    
    nombre_archivo = f"{siguiente_numero}Clase-{fecha_str}.md"
    return siguiente_numero, nombre_archivo

def procesar_y_guardar_nota_gui(texto_total, nombre_carpeta, nombre_materia):
    """
    Ejecuta el formateo final con Gemini y guarda la nota usando 
    la misma secuencia exacta de tu código CLI original.
    """
    ruta_completa = os.path.join(RUTA_NOTAS, nombre_carpeta)
    num_clase, nombre_archivo = obtener_siguiente_nombre_clase(ruta_completa)
    ruta_archivo_final = os.path.join(ruta_completa, nombre_archivo)

    # Llamada a Gemini respetando la firma original de tu core:
    # procesar_con_gemini(texto_total, nombre_carpeta, num_clase, nombre_materia)
    apunte_formateado = procesar_con_gemini(texto_total, nombre_carpeta, num_clase, nombre_materia)

    with open(ruta_archivo_final, "w", encoding="utf-8") as f:
        f.write(apunte_formateado)

    if os.path.exists(ARCHIVO_TEMP):
        os.remove(ARCHIVO_TEMP)

    return ruta_archivo_final

def obtener_carpetas_disponibles():
    """Retorna la lista de carpetas para llenar el OptionMenu de la GUI."""
    if not os.path.exists(RUTA_NOTAS):
        return []
    carpetas = [f for f in os.listdir(RUTA_NOTAS) if os.path.isdir(os.path.join(RUTA_NOTAS, f))]
    carpetas.sort()
    return carpetas

  
def guardar_estado_temporal(carpeta, materia, transcripcion):
    """Guarda o actualiza la metadata y la transcripción en el archivo temporal."""
    datos = {
        "carpeta": carpeta,
        "materia": materia,
        "transcripcion": transcripcion
    }
    with open(ARCHIVO_TEMP_JSON, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)

def leer_estado_temporal():
    """Lee la información resguardada en el archivo temporal."""
    if not os.path.exists(ARCHIVO_TEMP_JSON):
        return None
    try:
        with open(ARCHIVO_TEMP_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Error al leer temporal]: {e}")
        return None

def eliminar_estado_temporal():
    """Elimina el respaldo cuando la nota se guarda con éxito."""
    if os.path.exists(ARCHIVO_TEMP_JSON):
        os.remove(ARCHIVO_TEMP_JSON)

def procesar_y_guardar_nota_gui(texto_total, nombre_carpeta, nombre_materia):
    """Procesa el apunte con Gemini y limpia el archivo de respaldo al finalizar."""
    ruta_completa = os.path.join(RUTA_NOTAS, nombre_carpeta)
    if not os.path.exists(ruta_completa):
        os.makedirs(ruta_completa, exist_ok=True)

    num_clase, nombre_archivo = obtener_siguiente_nombre_clase(ruta_completa)
    ruta_archivo_final = os.path.join(ruta_completa, nombre_archivo)

    apunte_formateado = procesar_con_gemini(texto_total, nombre_carpeta, num_clase, nombre_materia)

    with open(ruta_archivo_final, "w", encoding="utf-8") as f:
        f.write(apunte_formateado)

    # Limpiar el respaldo automático tras guardar
    eliminar_estado_temporal()

    return ruta_archivo_final

def recuperar_nota(status_callback=None):
    """Recupera la nota pendiente usando automáticamente la carpeta y prompt guardados."""
    def notificar(mensaje):
        if status_callback:
            status_callback(mensaje)

    datos = leer_estado_temporal()
    if not datos:
        notificar("No se encontró ningún respaldo de nota pendiente.")
        return

    transcripcion = datos.get("transcripcion", "").strip()
    carpeta = datos.get("carpeta", "General")
    materia = datos.get("materia", "General")

    if not transcripcion:
        notificar("El archivo de respaldo está vacío.")
        return

    notificar(f"Reintentando apunte para '{materia}' en la carpeta '{carpeta}'...")

    try:
        ruta_final = procesar_y_guardar_nota_gui(transcripcion, carpeta, materia)
        notificar(f"¡Nota recuperada con éxito en Obsidian!\n[{os.path.basename(ruta_final)}]")
    except Exception as e:
        notificar(f"[ERROR]: Falló la API. Se conserva el respaldo de la nota.") 

