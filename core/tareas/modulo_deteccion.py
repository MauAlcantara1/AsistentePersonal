import re
import unicodedata
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import random
from rapidfuzz import fuzz

INTENCIONES = {
    "VER TAREAS": {
        "palabras": [
            "ver mis tareas", "mostrar tareas", "que tengo que hacer",
            "listar tareas", "cuales son mis tareas", "revisar pendientes",
            "mostrar pendientes", "ver la lista de tareas", "agenda de hoy",
            "cual es mi tarea hoy", "cuales son mis tareas de hoy",
            "que tareas tengo hoy", "dime mis tareas", "cuales son mis pendientes de hoy",
            "que pendientes tengo", "muestrame mis tareas de hoy",
            "que me falta por hacer", "dime que pendientes tengo",
            "checa mis tareas", "revisa mi lista de tareas",
            "cuantas tareas tengo pendientes", "que tengo pendiente hoy",
            "cuales son mis pendientes", "muestrame la lista de pendientes",
            "dame un resumen de mis tareas", "que actividades tengo hoy",
            "cual es mi agenda", "recuerdame que tengo que hacer",
            "que hay en mi lista de tareas", "tengo tareas pendientes",
            "dime que tengo pendiente"
        ],
        "requiere_verificacion": True
    },

    "ANADIR_TAREAS": {
        "palabras": [
            "agregar tarea", "anadir tarea", "crear tarea", "guardar tarea",
            "anade una tarea", "agrega a mi lista", "recordarme hacer",
            "nueva tarea", "anadir pendiente", "anade un recordatorio",
            "agrega a mi lista de pendientes la tarea de",
            "anade la tarea de x a la base", "anadir una tarea a la base",
            "hay que anadir una nueva tarea", "guarda esta tarea en la base",
            "registra una nueva tarea", "apunta una tarea nueva",
            "anademe una tarea", "agregame una tarea nueva",
            "pon una tarea en mi lista", "necesito agregar una tarea",
            "quiero agregar un pendiente", "mete esta tarea a la lista",
            "suma una tarea a mi lista", "crea un nuevo pendiente",
            "guardame esta tarea", "anota esta tarea en mis pendientes",
            "agrega la tarea de", "recuerdame que tengo que hacer x",
            "agenda una tarea para", "necesito que agregues una tarea"
        ],
        "requiere_verificacion": True
    },

    "QUITAR_TAREA": {
        "palabras": [
            "eliminar tarea", "borrar tarea", "quitar tarea", "completar tarea",
            "marcar como hecha", "tachar tarea", "remover tarea", "borra la tarea",
            "elimina el pendiente", "quitar de la lista",
            "marca la tarea como hecha de", "ya termine la tarea de",
            "quita esta tarea de la lista", "borra el pendiente de",
            "ya hice la tarea de", "esa tarea ya la termine",
            "marca como completada la tarea de", "dala por terminada la tarea de",
            "elimina esa tarea de mi lista", "quita el pendiente de",
            "borra esa tarea", "ya acabe con la tarea de",
            "puedes eliminar la tarea de", "tacha el pendiente de",
            "esa tarea ya esta lista", "remueve el pendiente de",
            "marca como hecho el pendiente de"
        ],
        "requiere_verificacion": True
    },

    "REPRODUCIR_MUSICA": {
        "palabras": [
            "pon musica", "reproducir musica", "reproduce una cancion",
            "pon la cancion", "escuchar musica", "pon algo de musica",
            "iniciar reproduccion", "poner lista de reproduccion",
            "ponme una cancion", "quiero escuchar musica",
            "reproduce el album de", "pon algo de rap",
            "pon algo de rock", "pon musica de", "ponme algo para relajarme",
            "reproduce mi playlist", "pon mi lista de reproduccion",
            "quiero escuchar una cancion de", "pon algo movido",
            "ponme musica para trabajar", "reproduce algo de",
            "pon el nuevo disco de", "quiero oir musica"
        ],
        "requiere_verificacion": False
    },

    "DETENER_MUSICA": {
        "palabras": [
            "pausa la musica", "detener musica", "para la musica",
            "quita la musica", "silencia la musica", "pausa la cancion",
            "detén la reproduccion", "para de reproducir musica",
            "ya no quiero escuchar musica", "apaga la musica",
            "stop a la musica", "baja la musica y detente"
        ],
        "requiere_verificacion": False
    },

    "SALUDO": {
        "palabras": [
            "hola", "buenos dias", "buenas tardes", "buenas noches",
            "que tal", "como estas", "saludos", "hola agnes", "hey",
            "hola como estas", "que onda", "buen dia", "hola que tal",
            "hey agnes", "todo bien", "quiubo", "hola buenas"
        ],
        "requiere_verificacion": False
    },

    "DESPEDIDA": {
        "palabras": [
            "adios", "hasta luego", "nos vemos", "me voy",
            "chao", "hasta pronto", "eso es todo por ahora",
            "ya no necesito nada mas", "gracias eso es todo",
            "nos vemos luego", "hasta manana", "me despido",
            "eso seria todo", "ya me voy", "hasta la proxima"
        ],
        "requiere_verificacion": False
    },

    "BUSCA_YOUTUBE_SOBRE": {
        "palabras": [
            "busca en youtube", "reproduce en youtube", "ver en youtube",
            "busca el video de", "pon el video", "buscar video", "pon en youtube",
            "pon un video sobre", "puedes poner un video sobre",
            "quiero ver un video de", "muestrame un video sobre",
            "busca un video sobre", "pon un video de youtube",
            "buscame un video de", "quiero ver algo sobre en youtube",
            "pon un tutorial de", "busca un tutorial sobre",
            "ensename un video de", "abre youtube y busca",
            "quiero ver videos de", "pon el ultimo video de"
        ],
        "requiere_verificacion": False
    },

    "GUARDAR_NOTA": {
        "palabras": [
            "anota esto", "guarda esta nota", "crear una nota", "anotar",
            "toma nota de", "haz una nota de", "agrega una nota",
            "guarda una nota rapida", "anota lo siguiente", "registra esta nota",
            "apunta esto", "guarda una nota que diga", "anota que tengo que",
            "crea una nota rapida", "anota", "guarda la nota", "nueva nota",
            "quiero anotar algo", "guardame esta idea", "anota esta idea",
            "crea una nota con esto", "toma nota rapida",
            "necesito anotar algo", "escribeme una nota que diga",
            "guarda este pensamiento", "apunta lo que voy a decir",
            "hazme una nota de esto"
        ],
        "requiere_verificacion": False
    },

    "VER_NOTAS": {
        "palabras": [
            "ver mis notas", "mostrar notas", "quecosas anote", "cuales son mis notas",
            "leer mis notas", "mis notas de hoy", "mostrar notas rapidas",
            "que notas tengo", "dime mis notas", "revisar notas",
            "cuales notas tengo guardadas", "que anote hoy", "muestrame las notas",
            "lee mis notas", "que tengo anotado", "dime que anote",
            "cuales son mis notas de hoy", "checa mis notas",
            "muestrame mis notas guardadas", "que notas tengo guardadas",
            "dame un resumen de mis notas"
        ],
        "requiere_verificacion": False
    },

    "BUSCA_INFORMACION": {
        "palabras": [
            "busca en internet", "busca informacion sobre", "quien es",
            "que es", "investiga sobre", "googlea", "buscar en la web",
            "dame informacion de",
            "buscame informacion sobre", "que sabes de", "investigame sobre",
            "puedes buscar informacion de", "que significa",
            "dame datos sobre", "explicame que es", "busca datos de",
            "quiero saber sobre", "dime sobre"
        ],
        "requiere_verificacion": False
    },

    "CLIMA": {
        "palabras": [
            "como esta el clima", "que clima hace hoy", "va a llover hoy",
            "cual es el pronostico del tiempo", "dime el clima",
            "como esta el tiempo hoy", "hace frio o calor hoy",
            "va a hacer frio hoy", "necesito paraguas hoy",
            "como amanece el dia", "cual es el pronostico de hoy",
            "que temperatura hace", "dime el pronostico del clima",
            "como va a estar el clima manana", "va a llover mas tarde"
        ],
        "requiere_verificacion": False
    },

    "HORA": {
        "palabras": [
            "que hora es", "dime la hora", "me dices la hora",
            "cual es la hora actual", "que hora tenemos",
            "podrias decirme la hora", "sabes que hora es",
            "checa la hora", "dame la hora exacta"
        ],
        "requiere_verificacion": False
    },

    "AYUDA": {
        "palabras": [
            "que puedes hacer", "que sabes hacer", "en que me puedes ayudar",
            "cuales son tus funciones", "dime que funciones tienes",
            "como te uso", "que comandos entiendes",
            "ayuda", "necesito ayuda", "que tareas puedes realizar",
            "muestrame que puedes hacer", "explica tus funciones"
        ],
        "requiere_verificacion": False
    },

    "CANCELAR": {
        "palabras": [
            "cancela eso", "olvidalo", "ya no importa", "cancela la accion",
            "dejalo asi", "mejor no", "ya no quiero hacer eso",
            "cancela lo anterior", "olvida lo que dije", "ya no",
            "detente", "cancela por favor"
        ],
        "requiere_verificacion": False
    }
}
_corpus = []
_intenciones_map = []

for intencion, datos in INTENCIONES.items():
    for frase in datos["palabras"]:
        _corpus.append(frase)
        _intenciones_map.append(intencion)

_vectorizer = TfidfVectorizer()
_X_corpus = _vectorizer.fit_transform(_corpus)

def normalizar_texto(texto: str) -> str:
    texto = texto.lower()
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    texto = re.sub(r'[^a-z0-9\s]', '', texto)
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto


def lematizar_verbos_basico(texto: str) -> str:
    reemplazos = {
        r'\bagrega\b|\bagregar\b|\banada\b|\banade\b|\banadir\b': 'anadir',
        r'\bmuestrame\b|\bmuestra\b|\bmostrar\b|\bver\b|\bleer\b': 'ver',
        r'\bquita\b|\bquitar\b|\bborra\b|\bborrar\b|\belimina\b|\beliminar\b': 'quitar',
        r'\bpon\b|\bponer\b|\breproduce\b|\breproducir\b': 'reproducir',
        r'\bbusca\b|\bbuscar\b|\binvestiga\b|\binvestigar\b': 'buscar',
        r'\banota\b|\banotar\b|\bapunta\b|\bapuntar\b|\bregistra\b|\bregistrar\b': 'anotar'
    }
    for patron, reemplazo in reemplazos.items():
        texto = re.sub(patron, reemplazo, texto)
    return texto

def preprocesar_entrada(texto: str) -> str:
    texto_limpio = normalizar_texto(texto)
    return lematizar_verbos_basico(texto_limpio)

def detectar_intencion(texto_usuario: str, umbral_coseno: float = 0.55):
    """
    Evalúa primero con Cosine Similarity. Si el puntaje es bajo, usa RapidFuzz como fallback.
    Retorna: (nombre_intencion, requiere_verificacion, score)
    """
    if not texto_usuario or not texto_usuario.strip():
        return "DESCONOCIDO", False, 0.0

    texto_prep = preprocesar_entrada(texto_usuario)
    
    vector_entrada = _vectorizer.transform([texto_prep])
    similitudes = cosine_similarity(vector_entrada, _X_corpus)[0]
    best_idx = np.argmax(similitudes)
    score_coseno = similitudes[best_idx]

    if score_coseno >= umbral_coseno:
        intencion = _intenciones_map[best_idx]
        req_verif = INTENCIONES[intencion]["requiere_verificacion"]
        return intencion, req_verif, round(float(score_coseno), 2)

    mejores_scores = []
    for intencion, datos in INTENCIONES.items():
        for frase in datos["palabras"]:
            ratio = fuzz.partial_ratio(texto_prep, frase) / 100.0
            mejores_scores.append((intencion, ratio))

    intencion_fuzz, score_fuzz = max(mejores_scores, key=lambda x: x[1])
    
    if score_fuzz >= 0.60:
        req_verif = INTENCIONES[intencion_fuzz]["requiere_verificacion"]
        return intencion_fuzz, req_verif, round(score_fuzz, 2)

    return "DESCONOCIDO", False, 0.0