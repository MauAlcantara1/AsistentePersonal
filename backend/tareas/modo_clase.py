import os
import re
import sys
import time
import threading
from datetime import datetime
from google import genai
from dotenv import load_dotenv

RUTA_NOTAS = "/home/mau-alcantara/Escritorio/clases/Notas"
ARCHIVO_TEMP = "temp_transcripcion.txt"
load_dotenv()  
grabando = True
pausasado = False
regresar_menu = False

def monitor_teclado():
    global grabando, pausado, regresar_menu

    print("\n  [CONTROLES DE CLASE]")
    print("  --> Presiona 'c' y ENTER para PAUSAR / REANUDAR la escucha")
    print("  --> Presiona 'p' y ENTER para FINALIZAR la clase y generar la nota\n")
    print("  --> Presiona 'r' y ENTER para CANCELAR y REGRESAR al menú principal\n")

    while grabando:
        try:
            comando = input().strip().lower()
            if comando == 'c':
                pausado = not pausado
                estado = "Pausa" if pausado else "Reanunado"
                print(f"\n[Sistema]: Grabacion {estado}\n")
            elif comando == 'p':
                print("\n[Sistema]: FInalizando grabacion....")
                print("Pasando al siguiente modulo no apagar")
                grabando = False
            elif comando == 'r':
                print("\n[Sistema]: Regresando al menu principal")
                regresar_menu = True
                grabando = False
        except EOFError:
            break

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

def seleccionar_carpeta_obsidian():
    if not os.path.exists(RUTA_NOTAS):
        print(f"Error: La ruta {RUTA_NOTAS} no existe.")
        return None, None

    carpetas = [f for f in os.listdir(RUTA_NOTAS) if os.path.isdir(os.path.join(RUTA_NOTAS, f))]
    carpetas.sort()

    if not carpetas:
        print("No se encontraron carpetas dentro de la ruta de Notas.")
        return None, None

    while True:
        print("\n--- Carpetas disponibles ---")
        for idx, carpeta in enumerate(carpetas, 1):
            print(f"{idx} - {carpeta}")

        opcion = input("\n Selecciona el numero de la carpeta"). strip()

        if not opcion.isdigit() or int(opcion) < 1 or int(opcion) > len(carpetas):
            print("Opcion invalidad. Intenta de nuevo")
            continue

        carpeta_seleccionada = carpetas[int(opcion) - 1]
        ruta_completa = os.path.join(RUTA_NOTAS, carpeta_seleccionada)

        archivos = os.listdir(ruta_completa)
        print(f"\nArchivos existentes en '{carpeta_seleccionada}'")
        for f in archivos:
            print(f" - {f}")

        confirmacion = input(f"\n¿Es correcta la carpeta ({carpeta_seleccionada})? (s/n):").strip().lower()
        if confirmacion == 's':
            return carpeta_seleccionada, ruta_completa

def procesar_con_gemini(transcripcion_raw, materia, num_clase):
    client = genai.Client()
    
    prompt = f"""
    Eres un experto organizador académico de apuntes para Obsidian.
    A continuación tienes la transcripción completa en bruto de una clase de '{materia}' (Clase #{num_clase}).

    Instrucciones de estructuración:
    1. Conservar explicaciones...
    2. Corregir errores evidentes del STT...
    3. Organizar jerárquicamente...
    4. Crear Mermaid cuando corresponda...
    5. Agregar YAML...
    6. Eliminar conversaciones o sonidos claramente ajenos a la clase.
    7. NO inventar información que no aparezca en la transcripción.
    8. Si una palabra o concepto es ambiguo y no puede corregirse con contexto,
    conservarlo de la forma más fiel posible.
    Transcripción:
    
    {transcripcion_raw}
    """
    
    response = client.models.generate_content(
        model='gemini-3.6-flash',
        contents=prompt
    )
    return response.text
def iniciar_modo_clase(sst_instance):
    global grabando, pausado
    grabando = True
    pausado = False

    materia, ruta_carpeta = seleccionar_carpeta_obsidian()
    if not materia:
        return

    num_clase, nombre_archivo = obtener_siguiente_nombre_clase(ruta_carpeta)
    ruta_archivo_final = os.path.join(ruta_carpeta, nombre_archivo)

    if os.path.exists(ARCHIVO_TEMP):
        os.remove(ARCHIVO_TEMP)

    print(f"\n[MODO CLASE ACTIVADO]")
    print(f"Materia: {materia}")
    print(f"Guardando en: {nombre_archivo}")

    hilo_teclado = threading.Thread(target=monitor_teclado, daemon=True)
    hilo_teclado.start()

    with open(ARCHIVO_TEMP, "a", encoding="utf-8") as f_temp:
        while grabando:
            if pausado:
                time.sleep(0.5)
                continue

            texto = sst_instance.listen()

            if texto and grabando and not pausado:
                print(f"[Escuchando]: {texto}")
                f_temp.write(texto + " ")
                f_temp.flush()

    if os.path.exists(ARCHIVO_TEMP):
        with open(ARCHIVO_TEMP, "r", encoding="utf-8") as f_temp:
            texto_total = f_temp.read().strip()

    else:
        texto_total = ""

    if not texto_total:
        print("No se detecto texto. Se cancelo la creacion de la nota")
        return

    print("Generando nota en Obsidian junto con Gemini :)")
    apunte_formateado = procesar_con_gemini(texto_total, materia, num_clase)

    with open(ruta_archivo_final, "w", encoding="utf-8") as f:
        f.write(apunte_formateado)
    if os.path.exists(ARCHIVO_TEMP):
        os.remove(ARCHIVO_TEMP)

    print(f"\n Apunte creado con Exito en Obsidian\n [{ruta_archivo_final}]")
        