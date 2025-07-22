import asyncio
from fastapi import WebSocket
from edge_tts.exceptions import NoAudioReceived
from features.speech.services.speech_service import SpeechService
from features.agent.services.agent_service import AgentService
from features.chat.services.transcription_service import TranscriptionService
from infrastructure.network.connection_manager import manager as conn_manager

class ChatService:
    """Orchestrates a single chat session, including transcription and messaging."""
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.buffer: list[bytes] = []
        self.lock = asyncio.Lock()
        self.agent_service = AgentService()
        self.speech_service = SpeechService()

    async def append_audio(self, chunk: bytes):
        """Appends an audio chunk to the buffer."""
        async with self.lock:
            self.buffer.append(chunk)

    async def handle_stop_event(self):
        """Processes the buffered audio when a 'stop' event is received."""
        async with self.lock:
            if not self.buffer:
                return
            pcm_data = b''.join(self.buffer)
            self.buffer.clear()

        user_transcribed_speech = await TranscriptionService.transcribe_audio(pcm_data)
        await self.send_text("user", user_transcribed_speech)

        agent_response, is_directed_at_agent = self.agent_service.get_response(user_transcribed_speech)
        if is_directed_at_agent and agent_response:
            await self.send_text("ai", agent_response)
            try:
                audio_bytes = await self.speech_service.text_to_speech(agent_response)
                await self.send_audio(audio_bytes)
            except NoAudioReceived as e:
                print("Skipping TTS for empty or invalid text.", e)
                pass
        else:
            await self.send_text("ai", "[Ignored: Not directed at agent]")

    async def send_text(self, role: str, text: str):
        """Sends a text message to the client."""
        await conn_manager.send_json({
            "type": "text",
            "role": role,
            "text": text
        }, self.websocket)

    async def send_audio(self, data: bytes):
        """Sends binary audio data to the client."""
        await conn_manager.send_bytes(data, self.websocket)
