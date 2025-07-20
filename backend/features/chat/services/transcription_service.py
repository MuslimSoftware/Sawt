from features.chat.repositories.transcription_repository import TranscriptionRepository
from features.common.types.exceptions import BaseSawtException

class TranscriptionService:
    @staticmethod
    async def transcribe_audio(pcm_bytes: bytes) -> str:
        try:
            result = await TranscriptionRepository.send_audio(pcm_bytes)
            return result.get('text', '')
        except Exception as e:
            raise BaseSawtException(
                code="TRANSCRIPTION_FAILED",
                message=str(e),
                status_code=500,
            )
