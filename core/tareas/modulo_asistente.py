from core.voice.texto_voz import SpeechToText
from core.voice.voz_texto import hablar
from core.tareas.modulo_respuesta import generar_respuesta
from core.tareas.modulo_deteccion import detectar_intencion
from dotenv import load_dotenv, set_key
import os
def inicio_uno():

    hablar("Estare aqui para ayudarte")
    while True:

        texto = stt.listen()

        if not texto:
            continue

        print(f"Usuario: {texto}")

        intencion, requiere_verificacion, score = detectar_intencion(texto)

        print(
            f"Intención detectada: {intencion} "
            f"(Confianza: {score})"
        )
        print(
            f"¿Requiere confirmación?: "
            f"{requiere_verificacion}"
        )

        respuesta = generar_respuesta(intencion)

        hablar(respuesta)

        #if intencion == "GUARDAR_NOTA":
         #   respuesta = escuchar_nota()
        #elif intencion == "VER_NOTAS":
         #   respuesta = obtener_notas_activas(usuario_id=1)
