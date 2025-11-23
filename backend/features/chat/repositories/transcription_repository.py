import os, asyncio, logging, struct
import numpy as np
import torch
from transformers import pipeline
from features.common.types.exceptions import BaseSawtException

PCM_RATE     = 16000
SAMPLE_WIDTH = 2  # bytes per sample (16‑bit mono)

# ── one‑time model load ────────────────────────────────────────────────
MODEL_ID = os.getenv("HUGGING_FACE_TRANSCRIPTION_MODEL", "openai/whisper-base")
device   = 0 if torch.cuda.is_available() else -1          # -1 → CPU
asr_pipe = pipeline(
    task="automatic-speech-recognition",
    model=MODEL_ID,
    device=device,
)

logger = logging.getLogger(__name__)

class TranscriptionRepository:
    @staticmethod
    async def transcribe(pcm_bytes: bytes) -> str:
        # 1️⃣  Save the incoming audio exactly like before -------------
        wav_bytes = TranscriptionRepository._wrap_wav(pcm_bytes)
        TranscriptionRepository._save_wav(wav_bytes)
        # -------------------------------------------------------------

        # 2️⃣  Run Whisper locally (non‑blocking for the event‑loop)
        loop  = asyncio.get_running_loop()
        audio = TranscriptionRepository._pcm_to_float32(pcm_bytes)

        try:
            result = await loop.run_in_executor(
                None, lambda: asr_pipe(audio, chunk_length_s=30, stride_length_s=5)
            )
            return result["text"]
        except Exception as e:
            logger.exception("Error transcribing audio")
            raise BaseSawtException(
                code="TRANSCRIPTION_FAILED",
                message=str(e),
                status_code=500,
            )

    # ── helpers ────────────────────────────────────────────────────────
    @staticmethod
    def _pcm_to_float32(pcm_bytes: bytes) -> np.ndarray:
        """Convert 16‑bit PCM to float32 in the range ‑1…1."""
        data = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32)
        return data / 32768.0

    @staticmethod
    def _wrap_wav(pcm: bytes) -> bytes:
        """Wrap raw PCM in a minimal 16 kHz mono WAV container."""
        return struct.pack(
            "<4sI4s4sIHHIIHH4sI",
            b"RIFF",
            36 + len(pcm),
            b"WAVE",
            b"fmt ",
            16,
            1,           # PCM format
            1,           # channels
            PCM_RATE,
            PCM_RATE * SAMPLE_WIDTH,
            SAMPLE_WIDTH,
            8 * SAMPLE_WIDTH,
            b"data",
            len(pcm),
        ) + pcm

    @staticmethod
    def _save_wav(wav: bytes, filename: str = "current_audio.wav") -> None:
        """Write the WAV to tmp/current_audio.wav (creates tmp/ if needed)."""
        tmp_dir = os.path.join(os.getcwd(), "tmp")
        os.makedirs(tmp_dir, exist_ok=True)
        with open(os.path.join(tmp_dir, filename), "wb") as f:
            f.write(wav)
