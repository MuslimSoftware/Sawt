import os
import aiohttp
import struct
import json
from features.common.types.exceptions import BaseSawtException

HF_TOKEN = os.getenv("HUGGING_FACE_API_TOKEN")
MODEL_ID = os.getenv("HUGGING_FACE_TRANSCRIPTION_MODEL")
HF_URL = f"https://api-inference.huggingface.co/models/{MODEL_ID}"

PCM_RATE = 16000
SAMPLE_WIDTH = 2  # bytes per sample (16-bit mono)

class TranscriptionRepository:
    @staticmethod
    async def transcribe(pcm_bytes: bytes) -> str:
        """Send raw 16kHz mono 16-bit PCM to Hugging Face and return transcription text."""
        wav = TranscriptionRepository._wrap_wav(pcm_bytes)
        headers = {
            "Authorization": f"Bearer {HF_TOKEN}",
            "Content-Type": "audio/wav"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(HF_URL, data=wav, headers=headers) as r:
                    body = await r.text()
                    if r.status != 200:
                        raise RuntimeError(f"HuggingFace error {r.status}: {body}")
                    data = json.loads(body)

            # HF ASR returns either {"text": "..."} or a list of segments; handle both.
            if isinstance(data, dict) and "text" in data:
                return data["text"]
            if isinstance(data, list):
                return "".join(part.get("text", "") for part in data)
        except Exception as e:
            raise BaseSawtException(
                code="TRANSCRIPTION_FAILED",
                message=str(e),
                status_code=500,
            )

    @staticmethod
    def _wrap_wav(pcm: bytes) -> bytes:
        """Wrap raw PCM in a minimal WAV container."""
        return struct.pack(
            "<4sI4s4sIHHIIHH4sI",
            b"RIFF",
            36 + len(pcm),
            b"WAVE",
            b"fmt ",
            16,
            1,              # PCM
            1,              # channels
            PCM_RATE,
            PCM_RATE * SAMPLE_WIDTH,
            SAMPLE_WIDTH,
            8 * SAMPLE_WIDTH,
            b"data",
            len(pcm),
        ) + pcm
