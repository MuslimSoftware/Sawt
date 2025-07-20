from features.chat.repositories.transcription_repository import TranscriptionRepository
from features.common.types.exceptions import BaseSawtException

import struct

PCM_RATE = 16000
SAMPLE_WIDTH = 2

class TranscriptionService:
    @staticmethod
    async def transcribe_audio(pcm_bytes: bytes) -> str:
        try:
            wav_bytes = TranscriptionService.build_wav(pcm_bytes)
            result = await TranscriptionRepository.send_audio(wav_bytes)
            return result.get('text', '')
        except Exception as e:
            raise BaseSawtException(
                code="TRANSCRIPTION_FAILED",
                message=str(e),
                status_code=500,
            )
    
    @staticmethod
    def build_wav(pcm_bytes: bytes) -> bytes:
        """Wrap raw PCM in a minimal WAV container."""
        num_samples = len(pcm_bytes) // SAMPLE_WIDTH
        return struct.pack(
            '<4sI4s4sIHHIIHH4sI',
            b'RIFF',
            36 + len(pcm_bytes),
            b'WAVE',
            b'fmt ',
            16,
            1,
            1,
            PCM_RATE,
            PCM_RATE * SAMPLE_WIDTH,
            SAMPLE_WIDTH,
            8 * SAMPLE_WIDTH,
            b'data',
            len(pcm_bytes),
        ) + pcm_bytes
