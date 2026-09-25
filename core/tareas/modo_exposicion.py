import os
import time
import threading

from google import genai
from google.genai.errors import ServerError, APIError
from dotenv import load_dotenv

from core.voice.voz_texto import hablar


ARCHIVO_TEMP = "temp_exposicion.txt"

load_dotenv()

grabando = True
pausado = False
regresar_menu = False

def menu():
    global grabando, pausado, regresar_menu

    print("\n  [CONTROLES DE EXPOSICIÓN]")
    print("  --> 'c' + ENTER = PAUSAR / REANUDAR")
    print("  --> 'p' + ENTER = FINALIZAR Y GENERAR RETROALIMENTACIÓN")
    print("  --> 'r' + ENTER = CANCELAR Y REGRESAR AL MENÚ\n")

    while grabando:
        try:
            comando = input().strip().lower()

            if comando == "c":
                pausado = not pausado

                if pausado:
                    hablar("Sistema en pausa")
                    print("[PAUSADO]")
                else:
                    hablar("Sistema reanudado")
                    print("[REANUDADO]")

            elif comando == "p":
                hablar(
                    "Generando la retroalimentacion, "
                    "espera un momento"
                )

                grabando = False

            elif comando == "r":
                hablar("Saliendo de la exposicion")

                regresar_menu = True
                grabando = False

        except EOFError:
            break

def escuchar_tema(sst_instance):

    hablar("¿Cuál es el tema de tu exposición?")

    tema = sst_instance.listen()

    if not tema:
        print("No se detectó el tema.")
        return None

    tema = tema.strip().lower()

    print(f"\nTema: {tema}")

    return tema

def escuchar_conceptos_clave(sst_instance):

    hablar(
        "Ahora dime cuáles son los conceptos clave "
        "que debe contener tu exposición"
        "con esto podre saber con mayor presicion sobre la exposicion"
    )

    conceptos = sst_instance.listen()

    if not conceptos:
        print("No se detectaron conceptos.")
        return []

    conceptos = conceptos.strip()

    print(f"\nConceptos clave: {conceptos}")

    # Convertimos la respuesta en una lista
    conceptos_lista = [
        concepto.strip()
        for concepto in conceptos.split(",")
        if concepto.strip()
    ]

    return conceptos_lista

def escuchar_exposicion(sst_instance):

    global grabando, pausado

    texto_total = []

    # Limpiar archivo anterior
    with open(ARCHIVO_TEMP, "w", encoding="utf-8"):
        pass

    hilo_teclado = threading.Thread(
        target=menu,
        daemon=True
    )

    hilo_teclado.start()

    print("\n========== EXPOSICIÓN ==========\n")

    while grabando:

        if pausado:
            time.sleep(0.5)
            continue

        texto = sst_instance.listen()

        if texto and grabando and not pausado:

            texto = texto.strip()

            print(f"Escuchando: {texto}")

            texto_total.append(texto)

            # Guardar inmediatamente
            with open(
                ARCHIVO_TEMP,
                "a",
                encoding="utf-8"
            ) as f_temp:

                f_temp.write(texto + "\n")
                f_temp.flush()

    return "\n".join(texto_total)


def procesar_con_gemini(
    transcripcion_raw,
    tema,
    conceptos,
    retries=4,
    delay=5
):

    client = genai.Client()

    conceptos_texto = ", ".join(conceptos)

    prompt = f"""
Eres un evaluador experto en exposiciones académicas.

Tu trabajo es analizar una exposición oral realizada por un estudiante.

TEMA DE LA EXPOSICIÓN:
{tema}

CONCEPTOS QUE DEBE CUBRIR:
{conceptos_texto}

TRANSCRIPCIÓN COMPLETA:
{transcripcion_raw}


Analiza la exposición y genera una retroalimentación
clara y útil para que el estudiante pueda mejorar.

Evalúa:

1. CONTENIDO
- ¿Explicó correctamente el tema?
- ¿Cubrió los conceptos importantes?
- ¿Hubo errores conceptuales?
- ¿Faltó información importante?

2. ESTRUCTURA
- Introducción
- Desarrollo
- Conclusión
- Orden lógico de las ideas

3. CLARIDAD
- Explicaciones confusas
- Conceptos que necesitan aclaración
- Uso de ejemplos

4. PUNTOS FUERTES
Identifica específicamente qué hizo bien.

5. PUNTOS A MEJORAR
Identifica problemas concretos.

6. ERRORES
Señala cualquier afirmación incorrecta.
Explica cuál sería la forma correcta.

7. RECOMENDACIONES
Dale consejos concretos para mejorar
la siguiente exposición.

8. CALIFICACIÓN
Da una calificación estimada de 0 a 100.

IMPORTANTE:

No inventes información que no aparezca
en la exposición.

Diferencia entre:
- errores reales
- información que simplemente no fue mencionada
- aspectos que podrían mejorarse.
- por la calidad del microfono ciertas palabras no pueden procesarse bien o trancribirse, si la palabrea dicha es similar pasala como buena, ejemplo poda/oda


Responde en español y utiliza títulos
y listas para facilitar la lectura.
"""

    for intento in range(1, retries + 1):

        try:

            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt
            )

            return response.text

        except (ServerError, APIError) as e:

            print(
                f"\n[Servidor ocupado] "
                f"Intento {intento}/{retries}"
            )

            if intento < retries:

                print(
                    f"Esperando {delay} segundos..."
                )

                time.sleep(delay)

            else:
                raise

def recuperar_nota():

    if not os.path.exists(ARCHIVO_TEMP):

        print(
            f"No se encontró el archivo "
            f"'{ARCHIVO_TEMP}'."
        )

        return None

    with open(
        ARCHIVO_TEMP,
        "r",
        encoding="utf-8"
    ) as f:

        texto_total = f.read().strip()

    if not texto_total:

        print("El archivo temporal está vacío.")

        return None

    return texto_total


def inicio(sst_instance):

    #Aqui estan las variables que se usaran para los hilos
    global grabando
    global pausado
    global regresar_menu

    grabando = True
    pausado = False
    regresar_menu = False

    hablar(
        "Hola. Te ayudaré a practicar tu exposición."
    )

    tema = escuchar_tema(sst_instance) #Se llama a la funcion para escuchar el tema

    if not tema:
        hablar("No pude obtener el tema.")
        return

    hablar(
        f"Perfecto. El tema será {tema}."
    )
    conceptos = escuchar_conceptos_clave( # Se llamara a la funcion para escuchar los principales conceptos clave
        sst_instance
    )

    if not conceptos:

        hablar(
            "No pude obtener los conceptos clave."
        )

        return

    hablar(
        f"Guardé el tema {tema} "
        f"y los conceptos clave."
    )


    hablar(
        "Cuando estés listo puedes comenzar."
    )

    texto_total = escuchar_exposicion(
        sst_instance
    )

    if regresar_menu:

        print("Exposición cancelada.")

        return

 
    if not texto_total.strip():

        hablar(
            "No se detectó texto durante la exposición."
        )

        return

    print("\n========== TRANSCRIPCIÓN ==========\n")
    print(texto_total)


    hablar(
        "Analizaré tu exposición. "
        "Esto puede tardar un momento."
    )

    try:

        retroalimentacion = procesar_con_gemini(
            texto_total,
            tema,
            conceptos
        )

        salida_retroalimentacion(retroalimentacion)

        print(
            "\n========== RETROALIMENTACIÓN ==========\n"
        )

        print(retroalimentacion)

        # Guardar resultado
        with open(
            "retroalimentacion_exposicion.txt",
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                f"# Exposición: {tema}\n\n"
            )

            f.write(
                "## Conceptos clave\n\n"
            )

            for concepto in conceptos:

                f.write(
                    f"- {concepto}\n"
                )

            f.write(
                "\n## Retroalimentación\n\n"
            )

            f.write(
                retroalimentacion
            )

        hablar(
            "La retroalimentacion terminó. "
            "También fue guardada."
        )

    except Exception as e:

        print(
            f"\nError procesando exposición: {e}"
        )

        hablar(
            "No pude generar la retroalimentacion. "
            "La exposicion fue guardada para intentarlo despues."
        )

def salida_retroalimentacion(retroalimentacion):
    print("\n¿Qué quieres hacer con la retroalimentación?")
    print("[1] Guardarla en un archivo")
    print("[2] Escucharla")

    opcion = input("Selecciona una opción: ").strip()

    if opcion == "1":
        ruta = input("Escribe la ubicación donde quieres guardarla: ").strip()

        try:
            with open(ruta, "w", encoding="utf-8") as archivo:
                archivo.write(retroalimentacion)

            print(f"\nRetroalimentación guardada en: {ruta}")
            hablar("La retroalimentación fue guardada correctamente.")

        except Exception as e:
            print(f"Error al guardar: {e}")
            hablar("Ocurrió un error al guardar la retroalimentación.")

    elif opcion == "2":
        hablar(retroalimentacion)

    else:
        print("Opción no válida.")
        hablar("La opción seleccionada no es válida.")