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
            # nuevas, tomadas del log real
            "cual es mi tarea hoy", "cuales son mis tareas de hoy",
            "que tareas tengo hoy", "dime mis tareas", "cuales son mis pendientes de hoy",
            "que pendientes tengo", "muestrame mis tareas de hoy"
        ],
        "requiere_verificacion": True
    },

    "ANADIR_TAREAS": {
        "palabras": [
            "agregar tarea", "anadir tarea", "crear tarea", "guardar tarea",
            "anade una tarea", "agrega a mi lista", "recordarme hacer",
            "nueva tarea", "anadir pendiente", "anade un recordatorio",
            # nuevas, tomadas del log real
            "agrega a mi lista de pendientes la tarea de",
            "anade la tarea de x a la base", "anadir una tarea a la base",
            "hay que anadir una nueva tarea", "guarda esta tarea en la base",
            "registra una nueva tarea", "apunta una tarea nueva"
        ],
        "requiere_verificacion": True
    },

    "QUITAR_TAREA": {
        "palabras": [
            "eliminar tarea", "borrar tarea", "quitar tarea", "completar tarea",
            "marcar como hecha", "tachar tarea", "remover tarea", "borra la tarea",
            "elimina el pendiente", "quitar de la lista",
            # nuevas, para reforzar el contraste con anadir
            "marca la tarea como hecha de", "ya termine la tarea de",
            "quita esta tarea de la lista", "borra el pendiente de"
        ],
        "requiere_verificacion": True
    },

    "REPRODUCIR_MUSICA": {
        "palabras": [
            "pon musica", "reproducir musica", "reproduce una cancion",
            "pon la cancion", "escuchar musica", "pon algo de musica",
            "iniciar reproduccion", "poner lista de reproduccion",
            "ponme una cancion", "quiero escuchar musica",
            "reproduce el album de", "pon algo de rap"
            # Nota: quité la frase suelta "reproducir" —
            # es demasiado genérica y "ganaba" por si sola contra BUSCA_YOUTUBE_SOBRE.
        ],
        "requiere_verificacion": False
    },

    "SALUDO": {
        "palabras": [
            "hola", "buenos dias", "buenas tardes", "buenas noches",
            "que tal", "como estas", "saludos", "hola agnes", "hey"
        ],
        "requiere_verificacion": False
    },

    "BUSCA_YOUTUBE_SOBRE": {
        "palabras": [
            "busca en youtube", "reproduce en youtube", "ver en youtube",
            "busca el video de", "pon el video", "buscar video", "pon en youtube",
            # nuevas, tomadas del log real
            "pon un video sobre", "puedes poner un video sobre",
            "quiero ver un video de", "muestrame un video sobre",
            "busca un video sobre", "pon un video de youtube"
        ],
        "requiere_verificacion": False
    },

    "BUSCA_INFORMACION": {
        "palabras": [
            "busca en internet", "busca informacion sobre", "quien es",
            "que es", "investiga sobre", "googlea", "buscar en la web",
            "dame informacion de"
        ],
        "requiere_verificacion": False
    }
}

# --- Inicialización del Modelo TF-IDF al importar el módulo ---
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
        r'\bmuestrame\b|\bmuestra\b|\bmostrar\b|\bver\b': 'ver',
        r'\bquita\b|\bquitar\b|\bborra\b|\bborrar\b|\belimina\b|\beliminar\b': 'quitar',
        r'\bpon\b|\bponer\b|\breproduce\b|\breproducir\b': 'reproducir',
        r'\bbusca\b|\bbuscar\b|\binvestiga\b|\binvestigar\b': 'buscar'
    }
    for patron, reemplazo in reemplazos.items():
        texto = re.sub(patron, reemplazo, texto)
    return texto


def preprocesar_entrada(texto: str) -> str:
    texto_limpio = normalizar_texto(texto)
    return lematizar_verbos_basico(texto_limpio)

def detectar_intencion(texto_usuario: str, umbral_coseno: float = 0.25):
    """
    Evalúa primero con Cosine Similarity. Si el puntaje es bajo, usa RapidFuzz como fallback.
    Retorna: (nombre_intencion, requiere_verificacion, score)
    """
    if not texto_usuario or not texto_usuario.strip():
        return "DESCONOCIDO", False, 0.0

    texto_prep = preprocesar_entrada(texto_usuario)
    
    # 1. Intento por TF-IDF + Cosine Similarity
    vector_entrada = _vectorizer.transform([texto_prep])
    similitudes = cosine_similarity(vector_entrada, _X_corpus)[0]
    best_idx = np.argmax(similitudes)
    score_coseno = similitudes[best_idx]

    if score_coseno >= umbral_coseno:
        intencion = _intenciones_map[best_idx]
        req_verif = INTENCIONES[intencion]["requiere_verificacion"]
        return intencion, req_verif, round(float(score_coseno), 2)

    # 2. Fallback con RapidFuzz para transcripciones con ruido
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