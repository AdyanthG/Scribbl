import os
import uuid
from openai import OpenAI
from app.services.storage import StorageManager

class TTSEngine:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.storage = StorageManager()
        self.voice = "alloy" # Options: alloy, echo, fable, onyx, nova, shimmer

    def generate_audio(self, text: str) -> str:
        """
        Generates audio from text using OpenAI TTS.
        Returns local path to the audio file.
        """
        if not text:
            return None

        try:
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=self.voice,
                input=text
            )
            
            file_id = str(uuid.uuid4())
            tmp_path = f"/tmp/audio_{file_id}.mp3"
            
            response.stream_to_file(tmp_path)
            return tmp_path
            
        except Exception as e:
            print(f"TTS Error: {e}")
            return None
