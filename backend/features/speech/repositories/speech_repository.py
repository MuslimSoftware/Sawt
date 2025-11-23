from google.cloud import texttospeech
from google.oauth2 import service_account
from features.common.types.exceptions import ProviderException
import logging
import os
import json

logger = logging.getLogger(__name__)

class SpeechRepository:
    """Handles text-to-speech conversion using Google Cloud TTS."""

    def __init__(self):
        """Initialize the Google Cloud TTS client."""
        # Check for google_credentials environment variable
        if os.getenv("google_credentials"):
            try:
                credentials_info = json.loads(os.getenv("google_credentials"))
                credentials = service_account.Credentials.from_service_account_info(credentials_info)
                self.client = texttospeech.TextToSpeechClient(credentials=credentials)
                logger.info("Using credentials from google_credentials environment variable")
            except Exception as e:
                logger.error(f"Failed to load credentials from google_credentials: {e}")
                raise ProviderException(f"Failed to load Google Cloud credentials: {e}")
        else:
            logger.error("google_credentials environment variable not found")
            raise ProviderException("google_credentials environment variable not found")
        
        logger.info("Google Cloud TTS client initialized")

    async def synthesize(self, text: str) -> bytes:
        """
        Converts text to speech and returns the audio as bytes.
        """
        # Validate input
        if not text or not text.strip():
            logger.error("Empty or whitespace-only text provided for synthesis")
            raise ProviderException("Empty text provided for synthesis")
        
        logger.info(f"Starting TTS synthesis for text (length={len(text)}): {text[:200]}...")
        
        try:
            # Set the text input to be synthesized
            synthesis_input = texttospeech.SynthesisInput(text=text)

            # Build the voice request - using a male neural voice similar to Brian
            voice = texttospeech.VoiceSelectionParams(
                language_code="en-US",
                name="en-US-Neural2-J",  # Male neural voice
                ssml_gender=texttospeech.SsmlVoiceGender.MALE
            )

            # Select the audio file type
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )

            # Perform the text-to-speech request (synchronous in async context)
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )

            audio_bytes = response.audio_content
            logger.info(f"TTS synthesis successful. Generated {len(audio_bytes)} bytes of audio")
            return audio_bytes
            
        except Exception as e:
            logger.critical(f"Error synthesizing speech for text '{text[:100]}...': {str(e)}")
            raise ProviderException(message=str(e))