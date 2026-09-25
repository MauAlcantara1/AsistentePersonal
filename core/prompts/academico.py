from rapidfuzz import process, fuzz
from core.base_datos.conexion import obtener_conexion

PROMPT_APUNTES_GENERAL = """
Eres un experto organizador académico de apuntes para Obsidian.

Instrucciones generales:

1. Conservar las explicaciones importantes del profesor.
2. Corregir errores evidentes del STT.
3. Organizar la información jerárquicamente.
4. Crear diagramas Mermaid cuando corresponda.
5. Agregar YAML.
6. Eliminar conversaciones o sonidos claramente ajenos a la clase.
7. NO inventar información que no aparezca en la transcripción.
8. Si una palabra o concepto es ambiguo y no puede corregirse mediante
   contexto, conservarlo de la forma más fiel posible.
9. Las preguntas relacionadas con el tema deben conservarse y organizarse.
10. Eliminar preguntas o conversaciones que no estén relacionadas con la clase.
11. No colocar ```markdown al inicio del documento.
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