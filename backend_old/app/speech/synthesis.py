#!/usr/bin/env python3

import asyncio
import io
from typing import Optional

try:
    import edge_tts
except ImportError:
    print("⚠️  edge-tts not installed. Install with: pip install edge-tts")
    edge_tts = None

class TextToSpeechService:
    """TTS service using Microsoft Edge TTS"""
    
    def __init__(self, voice: str = "en-US-AriaNeural"):
        self.voice = voice
        if edge_tts is None:
            print(f"⚠️  Using placeholder TTS service with voice: {voice}")
            print("   Install edge-tts: pip install edge-tts")
        else:
            print(f"✅ TTS service initialized with voice: {voice}")
    
    async def synthesize_bytes(self, text: str) -> bytes:
        """Synthesize text to speech and return audio bytes"""
        if edge_tts is None:
            # Fallback to placeholder
            print(f"🔊 TTS (placeholder): '{text}'")
            return b""
        
        try:
            # Use Edge TTS to synthesize speech
            communicate = edge_tts.Communicate(text, self.voice)
            audio_data = io.BytesIO()
            
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data.write(chunk["data"])
            
            print(f"🔊 TTS: '{text}'")
            return audio_data.getvalue()
            
        except Exception as e:
            print(f"❌ TTS synthesis failed: {e}")
            return b""
    
    async def synthesize_file(self, text: str, filepath: str) -> None:
        """Synthesize text to speech and save to file"""
        audio_bytes = await self.synthesize_bytes(text)
        if audio_bytes:
            with open(filepath, 'wb') as f:
                f.write(audio_bytes) 