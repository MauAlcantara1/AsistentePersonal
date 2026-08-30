from voice.texto_voz import SpeechToText
from voice.voz_texto import hablar
from tareas.modulo_respuesta import generar_respuesta
from tareas.modulo_deteccion import detectar_intencion
from tareas.modo_clase import iniciar_modo_clase


stt = SpeechToText()
        
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

        print(f"Agnes: {respuesta}")

        hablar(respuesta)


def inicio_dos():
    """Modo Clase (Silencioso y en segundo plano)"""
    print("\n--- MODO CLASE ACTIVADO ---")
    iniciar_modo_clase(stt)


if __name__ == "__main__":
    hablar("Hola, mucho gusto soy tu asistente personal. Selecciona 1 para el modo normal o 2 para modo clase")

    while True:
        print("\n1. Modo Normal")
        print("2. Modo Clase")
        digito = input("Selecciona una opción (1/2): ").strip()

        if digito == "1":
            inicio_uno()
        elif digito == "2":
            inicio_dos()
        else:
            hablar("No es una opción válida")