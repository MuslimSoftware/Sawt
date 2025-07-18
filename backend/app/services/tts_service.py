#!/usr/bin/env python3

from typing import Optional
from app.repositories.tts_repository import TTSRepository

class TTSService:
    """High-level text-to-speech orchestration"""
    
    def __init__(self, repo: TTSRepository):
        self.repo = repo
    
    async def synthesize_response(self, text: str) -> Optional[bytes]:
        """Synthesize text to speech"""
        try:
            audio_bytes = await self.repo.synthesize_text(text)
            return audio_bytes
        except Exception as e:
            print(f"❌ TTS service error: {e}")
            return None 