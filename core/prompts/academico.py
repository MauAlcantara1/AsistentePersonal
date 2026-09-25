from rapidfuzz import process, fuzz
from core.base_datos.conexion import obtener_conexion

PROMPT_APUNTES_GENERAL = """
Eres un asistente experto en procesamiento de texto académico y generación de notas de clase estructuradas. Tu objetivo es procesar la transcripción de una clase adjunta y transformarla en un documento Markdown altamente detallado, limpio y organizado.

Sigue estrictamente las siguientes reglas:

1. EXPLICACIONES CLAVE: Consolida y conserva integrales todas las explicaciones importantes, conceptos teóricos, ejemplos y aclaraciones dadas por el profesor. Es preferible mantener un nivel alto de detalle a resumir en exceso.
2. CORRECCIÓN STT: Identifica y corrige errores evidentes de transcripción automática (Speech-to-Text), tales como palabras mal redactadas, homófonos, fallos de puntuación o jerga técnica mal transcrita, guiándote por el contexto académico.
3. ESTRUCTURA Y JERARQUÍA: Organiza toda la información en una jerarquía clara utilizando encabezados (##, ###), listas con viñetas y bloques de código según corresponda.
4. DIAGRAMAS MERMAID: Genera diagramas en sintaxis Mermaid (```mermaid ... ```) cuando la transcripción explique procesos, flujos de trabajo, arquitecturas, sistemas, algoritmos o jerarquías de conceptos.
5. METADATOS EN YAML: Inicia el documento obligatoriamente con un bloque de metadatos en formato YAML al principio del archivo (frontmatter entre ---) que incluya: título de la clase, temas principales, palabras clave y fecha/módulo si se menciona.
6. FILTRADO DE RUIDO: Elimina muletillas, interjecciones, sonidos ambientales transcritos, saludos iniciales de rutina o conversaciones casuales ajenas al tema académico.
7. FIDELIDAD (NO INVENTAR): NO inventes, asumas ni agregues información que no esté presente o respaldada directamente por la transcripción.
8. AMBIGÜEDAD Y DUDAS STT: Si una palabra, término técnico o concepto es ambiguo y el contexto no permite deducir la corrección exacta con certeza, consérvalo de la forma más fiel posible a como aparece transcrito.
9. PREGUNTAS DEL TEMA: Conserva y organiza en una sección dedicada (o integradas en su respectivo tema) todas las preguntas hechas por los alumnos que estén directamente relacionadas con la materia, junto con la respuesta dada por el profesor.
10. PREGUNTAS IRRELEVANTES: Elimina preguntas, interrupciones o discusiones que no aporten al contenido de la clase (p. ej., avisos administrativos ajenos, bromas, dudas de logística personal, risas).
11. FORMATO DE SALIDA: Entrega únicamente el contenido del documento. NO envuelvas todo el resultado en un bloque general de ```markdown al inicio ni al final del documento.

TRANSCRIPCIÓN A PROCESAR:
"""

def obtener_lista_materias_db():
    """Obtiene los nombres de materias desde PostgreSQL para la lista desplegable de la GUI."""
    try:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT nombre_materia FROM public.materias_prompts WHERE nombre_materia != 'generico' ORDER BY nombre_materia ASC;")
                filas = cur.fetchall()
                return [fila[0].title() for fila in filas]
    except Exception as e:
        print(f"[Error BD al obtener materias]: {e}")
        return ["General"]

def buscar_prompt_existente_db(nombre_ingresado, umbral_similitud=70):
    """Busca en PostgreSQL el prompt de la materia aplicando Fuzzy Matching."""
    if not nombre_ingresado or not nombre_ingresado.strip():
        return _obtener_prompt_generico_db()

    texto_limpio = nombre_ingresado.strip().lower()

    try:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT nombre_materia, prompt_instrucciones FROM public.materias_prompts;")
                filas = cur.fetchall()
                
                if not filas:
                    return _obtener_prompt_generico_db()

                materias_dict = {materia: prompt for materia, prompt in filas}

                # Coincidencia difusa para tolerar errores de escritura
                resultado = process.extractOne(
                    texto_limpio, 
                    list(materias_dict.keys()), 
                    scorer=fuzz.WRatio
                )

                if resultado and resultado[1] >= umbral_similitud:
                    materia_encontrada = resultado[0]
                    return materias_dict[materia_encontrada]

    except Exception as e:
        print(f"[Error BD al buscar prompt]: {e}")

    return None

def _obtener_prompt_generico_db():
    """Obtiene el prompt genérico directo de la base de datos."""
    try:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT prompt_instrucciones FROM public.materias_prompts WHERE nombre_materia = 'generico';")
                fila = cur.fetchone()
                if fila:
                    return fila[0]
    except Exception:
        pass
    return "Esta es una clase genérica. Organiza conceptos clave, definiciones y puntos principales."

def guardar_nueva_materia_db(nombre_materia, prompt_texto):
    """Guarda una nueva materia y su prompt generado en PostgreSQL."""
    materia_key = nombre_materia.strip().lower()
    try:
        with obtener_conexion() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO public.materias_prompts (nombre_materia, prompt_instrucciones)
                    VALUES (%s, %s)
                    ON CONFLICT (nombre_materia) DO UPDATE 
                    SET prompt_instrucciones = EXCLUDED.prompt_instrucciones;
                    """,
                    (materia_key, prompt_texto)
                )
            conn.commit()
            print(f"[Base de Datos]: Materia '{materia_key}' registrada con éxito en PostgreSQL.")
    except Exception as e:
        print(f"[Error BD al guardar materia]: {e}")