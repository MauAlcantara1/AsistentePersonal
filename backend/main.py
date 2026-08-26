from voice.texto_voz import SpeechToText
from voice.voz_texto import hablar
from tareas.modulo_respuesta import generar_respuesta
from tareas.modulo_deteccion import detectar_intencion

stt = SpeechToText()

print("Escuchando")
inicio = "Hola, soy Agnes. Tu asistente personal puedes decir ayuda si ocupas saber más de mi"

while True:

    hablar(inicio)

    print("\nEscuchando...")

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