import asyncio
import subprocess
import tempfile

import edge_tts


VOZ = "es-MX-DaliaNeural"


def hablar(texto: str):
    """
    Convierte texto a voz utilizando Edge TTS
    y reproduce el audio generado.
    """

    if not texto or not texto.strip():
        return

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=True) as archivo:

        async def generar_audio():
            comunicador = edge_tts.Communicate(
                texto,
                VOZ
            )

            await comunicador.save(archivo.name)

        asyncio.run(generar_audio())

        subprocess.run(
            ["mpv", "--no-video", archivo.name],
            check=True
        )