import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel

class SpeechToText:

    def __init__(self):
        self.model = WhisperModel(
            "small",
            device="cpu",
            compute_type="int8"
        )

    def listen(self, duration=5):

        audio = sd.rec(
            int(duration * 16000),
            samplerate=16000,
            channels=1,
            dtype="float32"
        )

        sd.wait()

        audio = np.squeeze(audio)

        segments, info = self.model.transcribe(
            audio,
            language="es"
        )

        texto = " ".join(segment.text for segment in segments)

        return texto.strip()