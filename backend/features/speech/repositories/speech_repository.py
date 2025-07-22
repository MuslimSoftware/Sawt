import asyncio
import edge_tts

class SpeechRepository:
    """Handles text-to-speech conversion using edge-tts."""

    async def synthesize(self, text: str) -> bytes:
        """
        Converts text to speech and returns the audio as bytes.
        """
        # In-memory buffer to hold the audio data
        audio_buffer = bytearray()

        # Use edge-tts to generate speech
        communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_buffer.extend(chunk["data"])

        return bytes(audio_buffer)
