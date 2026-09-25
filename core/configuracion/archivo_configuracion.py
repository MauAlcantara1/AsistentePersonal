import json
import os

ARCHIVO_CONFIG = "config.json"


def cargar_configuracion():
    if not os.path.exists(ARCHIVO_CONFIG):
        return {
            "ruta_boveda": ""
        }

    with open(ARCHIVO_CONFIG, "r", encoding="utf-8") as archivo:
        return json.load(archivo)


def guardar_configuracion(config):
    with open(ARCHIVO_CONFIG, "w", encoding="utf-8") as archivo:
        json.dump(config, archivo, indent=4, ensure_ascii=False)


def configurar_boveda(ruta, status_callback=None):

    def notificar(mensaje):
            if status_callback:
                status_callback(mensaje)

    if ruta == "s":
        return
    else:
        if not os.path.isdir(ruta):
            notificar("La ruta no es valida")
            return

        config = cargar_configuracion()
        config["ruta_boveda"] = ruta

        guardar_configuracion(config)

        notificar("La ruta fue guardada correctamente ")