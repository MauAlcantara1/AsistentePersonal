import random

RESPUESTAS = {

    "SALUDO": [
        "Hola, ¿en qué puedo ayudarte?",
        "Hola, ¿qué necesitas?",
        "Hola, dime qué necesitas.",
        "¡Hola! ¿Qué podemos hacer hoy?",
        "¡Qué tal! Aquí estoy para lo que necesites.",
        "¡Buen día! ¿En qué te puedo echar una mano?",
        "Hola, soy todo oídos.",
        "¡Hey! ¿Qué se te ofrece?",
        "Hola de nuevo, ¿en qué te ayudo?",
        "¡Qué gusto saludarte! ¿Qué necesitas?"
    ],

    "VER TAREAS": [
        "Claro, voy a revisar tus tareas.",
        "Por supuesto, voy a consultar tus tareas.",
        "Claro, voy a revisar tus pendientes.",
        "Dame un segundo, busco tu lista de pendientes.",
        "Enseguida te muestro lo que tienes por hacer.",
        "¡Listo! Aquí tienes las tareas que tienes apuntadas.",
        "Un momento, checando tu agenda...",
        "Ahí te va lo que tienes pendiente por hoy."
    ],

    "ANADIR_TAREAS": [
        "Claro, ¿qué tarea quieres añadir?",
        "Entendido, ¿qué tarea quieres agregar?",
        "Por supuesto, dime qué tarea quieres añadir.",
        "Perfecto, soy todo oídos. ¿Qué apunto en la lista?",
        "Listo para anotar, dime de qué se trata.",
        "Muy bien, ¿cuál es el nuevo pendiente?",
        "Dime la tarea y la agrego de inmediato.",
        "Va, ¿qué quieres que agregue a tu lista?"
    ],

    "QUITAR_TAREA": [
        "Claro, ¿qué tarea quieres quitar?",
        "Entendido, ¿qué tarea quieres eliminar?",
        "De acuerdo, dime qué tarea quieres quitar.",
        "Perfecto, ¿qué tarea tachamos de la lista?",
        "Dime el nombre de la tarea que ya terminaste.",
        "Muy bien, ¿cuál borramos?",
        "¡Buen trabajo! ¿Cuál tarea marco como hecha?",
        "Va, dime cuál pendiente eliminamos."
    ],

    "REPRODUCIR_MUSICA": [
        "Claro, voy a reproducir música.",
        "Entendido, voy a poner música.",
        "Por supuesto, voy a reproducir una canción.",
        "¡Excelente idea! Enseguida pongo algo de música.",
        "Preparando la música para ti...",
        "Subiendo el volumen. Vamos con un poco de música.",
        "Ahí va, disfruta la música.",
        "Dale, poniendo play ahora mismo."
    ],

    "BUSCA_YOUTUBE_SOBRE": [
        "Claro, voy a buscarlo en YouTube.",
        "Entendido, voy a buscar un video en YouTube.",
        "Por supuesto, voy a buscarlo en YouTube.",
        "A ver qué videos encontramos sobre eso...",
        "Abriendo YouTube para buscarlo enseguida.",
        "Dame un momento, busco los mejores videos al respecto.",
        "Enseguida te muestro un video sobre eso."
    ],

    "GUARDAR_NOTA": [
        "Claro, dime qué quieres que anote.",
        "Entendido, voy a guardar esa nota.",
        "Perfecto, dime qué anoto.",
        "Listo, adelante con lo que quieras anotar.",
        "Va, te escucho para tomar nota.",
        "Anotado quedará, dime qué es."
    ],

    "VER_NOTAS": [
        "Claro, voy a revisar tus notas.",
        "Por supuesto, buscando tus notas guardadas.",
        "Dame un segundo, reviso lo que tienes anotado.",
        "Enseguida te muestro tus notas.",
        "Aquí va lo que tienes guardado en tus notas."
    ],

    "BUSCA_INFORMACION": [
        "Claro, voy a buscar esa información.",
        "Entendido, voy a investigar sobre eso.",
        "Por supuesto, voy a buscar información.",
        "Dame un momento, consulto eso en la web.",
        "Voy a buscarlo en internet para darte la mejor respuesta.",
        "Averiguando... dame un segundito.",
        "Déjame investigar eso a fondo."
    ],

    # --- NUEVAS INTENCIONES SUGERIDAS ---
    "DESPEDIDA": [
        "¡Hasta luego! Que tengas un excelente día.",
        "Nos vemos, avísame si necesitas algo más.",
        "Adiós, aquí estaré por si me ocupas de nuevo.",
        "¡Chao! Cuídate mucho.",
        "Hasta pronto, fue un gusto ayudarte.",
        "Nos vemos luego, que te vaya muy bien."
    ],

    "CLIMA": [
        "Claro, voy a revisar el pronóstico del tiempo.",
        "Déjame asomarme a ver cómo está el clima.",
        "Enseguida te digo cómo está el clima afuera.",
        "Un momento, consultando el pronóstico.",
        "Ahí te va el reporte del clima."
    ],

    "HORA": [
        "Claro, te digo qué hora es.",
        "Déjame revisar el reloj.",
        "Enseguida te doy la hora exacta.",
        "Un segundo, checando la hora."
    ],

    "DESCONOCIDO": [
        "No estoy segura de qué necesitas.",
        "No logré entender lo que necesitas.",
        "No estoy segura de cómo ayudarte con eso.",
        "Mmm, creo que no te entendí del todo. ¿Puedes repetirlo?",
        "Lo siento, me perdí un poco. ¿Me lo explicas de otra forma?",
        "Aún no sé cómo hacer eso, pero sigo aprendiendo.",
        "Disculpa, ¿me lo puedes decir de otra manera?"
    ]
}
def generar_respuesta(intencion: str) -> str:
    """
    Genera una respuesta aleatoria y natural dependiendo de la intención detectada.
    """
    respuestas = RESPUESTAS.get(
        intencion,
        RESPUESTAS["DESCONOCIDO"]
    )

    return random.choice(respuestas)

# Ejemplo de uso:
# print(generar_respuesta("SALUDO"))
# print(generar_respuesta("ANADIR_TAREAS"))
# print(generar_respuesta("ALGO_INVENTADO"))