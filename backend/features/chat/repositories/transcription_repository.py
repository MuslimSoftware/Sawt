import os
import aiohttp

HF_URL = os.getenv("HF_URL")
HF_TOKEN = os.getenv("HF_TOKEN")

class TranscriptionRepository:
    @staticmethod
    async def send_audio(wav_bytes: bytes) -> dict:
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        async with aiohttp.ClientSession() as session:
            async with session.post(HF_URL, data=wav_bytes, headers=headers) as resp:
                resp.raise_for_status()
                return await resp.json()
