#!/usr/bin/env python3

from configs.speech_config import TTSConfig
from app.speech.synthesis import TextToSpeechService

class TTSRepository:
    """Low-level text-to-speech synthesis"""
    
    def __init__(self, config: TTSConfig):
        self.config = config
    
    async def synthesize_text(self, text: str) -> bytes:
        """Synthesize text to speech and return audio bytes"""
        try:
            tts_service = TextToSpeechService(self.config.voice)
            return await tts_service.synthesize_bytes(text)
        except Exception as e:
            print(f"❌ TTS synthesis failed: {e}")
            raise 