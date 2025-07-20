import os
import aiohttp
import struct

HF_URL = os.getenv("HF_URL")
HF_TOKEN = os.getenv("HF_TOKEN")

PCM_RATE = 16000
SAMPLE_WIDTH = 2

class TranscriptionRepository:
    @staticmethod
    async def send_audio(pcm_bytes: bytes) -> dict:
        wav_bytes = TranscriptionRepository.build_wav(pcm_bytes)

        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        async with aiohttp.ClientSession() as session:
            async with session.post(HF_URL, data=wav_bytes, headers=headers) as resp:
                resp.raise_for_status()
                return await resp.json()

    @staticmethod
    def build_wav(pcm_bytes: bytes) -> bytes:
        """Wrap raw PCM in a minimal WAV container."""
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