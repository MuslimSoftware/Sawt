import edge_tts
from features.common.types.exceptions import ProviderException
from edge_tts.exceptions import NoAudioReceived
import logging

logger = logging.getLogger(__name__)

class SpeechRepository:
    """Handles text-to-speech conversion using edge-tts."""

    async def synthesize(self, text: str) -> bytes:
        """
        Converts text to speech and returns the audio as bytes.
        """
        try:
            # In-memory buffer to hold the audio data
            audio_buffer = bytearray()

            # Use edge-tts to generate speech
            communicate = edge_tts.Communicate(text, "en-US-AvaMultilingualNeural")
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_buffer.extend(chunk["data"])

            return bytes(audio_buffer)
        except NoAudioReceived as e:
            logger.critical(f"No audio received: {str(e)}")
            raise ProviderException(message=str(e))
        except Exception as e:
            logger.critical(f"Error synthesizing speech: {str(e)}")
            raise ProviderException(message=str(e))