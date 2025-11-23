from features.speech.repositories.speech_repository import SpeechRepository

class SpeechService:
    """Service for text-to-speech conversion."""

    def __init__(self):
        self.repository = SpeechRepository()

    async def text_to_speech(self, text: str) -> bytes:
        """
        Converts text to speech.
        """
        return await self.repository.synthesize(text)
