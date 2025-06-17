#!/usr/bin/env python3

import edge_tts
import io
import soundfile as sf
import sounddevice as sd

# Available voices for text-to-speech
AVAILABLE_VOICES = [
    "en-US-ChristopherNeural",
    "en-US-EricNeural", 
    "en-US-GuyNeural",
    "en-US-RogerNeural",
    "en-US-SteffanNeural"
]

DEFAULT_VOICE = "en-US-ChristopherNeural"

async def speak(text: str, voice: str = DEFAULT_VOICE) -> None:
    """Convert text to speech and play it"""
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