from features.chat.repositories.transcription_repository import TranscriptionRepository
from features.common.types.exceptions import BaseSawtException

class TranscriptionService:
    @staticmethod
    async def transcribe_audio(pcm_bytes: bytes) -> str:
        transcription = await TranscriptionRepository.transcribe(pcm_bytes)
        return transcription
