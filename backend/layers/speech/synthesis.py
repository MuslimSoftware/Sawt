#!/usr/bin/env python3

import edge_tts
import io
import soundfile as sf
import sounddevice as sd
from typing import Optional

class TextToSpeechService:
    """Service for text-to-speech conversion using Edge TTS"""
    
    # Available voices for text-to-speech
    AVAILABLE_VOICES = [
        "en-US-ChristopherNeural",
        "en-US-EricNeural", 
        "en-US-GuyNeural",
        "en-US-RogerNeural",
        "en-US-SteffanNeural"
    ]
    
    DEFAULT_VOICE = "en-US-ChristopherNeural"
    
    def __init__(self, default_voice: str = DEFAULT_VOICE):
        """Initialize TTS service with default voice"""
        if default_voice not in self.AVAILABLE_VOICES:
            raise ValueError(f"Voice '{default_voice}' not available. Choose from: {self.AVAILABLE_VOICES}")
        self.default_voice = default_voice
        
    def get_available_voices(self) -> list[str]:
        """Get list of available voices"""
        return self.AVAILABLE_VOICES.copy()
        
    def validate_voice(self, voice: str) -> bool:
        """Validate if a voice is available"""
        return voice in self.AVAILABLE_VOICES
        
    async def speak(self, text: str, voice: Optional[str] = None) -> None:
        """Convert text to speech and play it"""
        voice = voice or self.default_voice
        if not self.validate_voice(voice):
            raise ValueError(f"Voice '{voice}' not available")
            
        try:
            communicate = edge_tts.Communicate(text, voice)
            audio_bytes = bytearray()
            
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_bytes.extend(chunk["data"])
            
            buffer = io.BytesIO(audio_bytes)
            data, samplerate = sf.read(buffer, dtype="float32")
            sd.play(data, samplerate)
            sd.wait()
        except Exception as e:
            print(f"❌ Text-to-speech error: {e}")
            raise

    async def synthesize_bytes(self, text: str, voice: Optional[str] = None) -> bytes:
        """Return TTS audio bytes (MP3) for the given text."""
        voice = voice or self.default_voice
        if not self.validate_voice(voice):
            raise ValueError(f"Voice '{voice}' not available")
            
        audio_bytes = bytearray()
        try:
            communicate = edge_tts.Communicate(text, voice)
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_bytes.extend(chunk["data"])
        except Exception as e:
            print(f"❌ TTS synth error: {e}")
            raise
        return bytes(audio_bytes)
        
    def set_default_voice(self, voice: str) -> None:
        """Set the default voice for TTS"""
        if not self.validate_voice(voice):
            raise ValueError(f"Voice '{voice}' not available")
        self.default_voice = voice 