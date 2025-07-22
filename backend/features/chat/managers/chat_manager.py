import asyncio
from fastapi import WebSocket
from features.chat.services.transcription_service import TranscriptionService
from infrastructure.network.connection_manager import manager as conn_manager

class ChatManager:
    """Handles audio buffering, transcription, and messaging via ConnectionManager."""
    def __init__(self):
        self.websocket: WebSocket | None = None
        self.buffer: list[bytes] = []
        self.lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        """Registers a new WebSocket client."""
        await conn_manager.connect(websocket)
        self.websocket = websocket

    async def disconnect(self):
        """Disconnects the current client."""
        if self.websocket:
            conn_manager.disconnect(self.websocket)
            self.websocket = None

    async def append_audio(self, chunk: bytes):
        async with self.lock:
            self.buffer.append(chunk)

    async def handle_stop(self):
        async with self.lock:
            pcm = b''.join(self.buffer)
            self.buffer.clear()

        text = await TranscriptionService.transcribe_audio(pcm)
        await self.send_text("user", text)

    async def send_text(self, role: str, text: str):
        """Sends a text JSON event via ConnectionManager."""
        if self.websocket:
            await conn_manager.send_json({"type": "text", "role": role, "text": text}, self.websocket)

    async def send_audio(self, data: bytes):
        """Sends binary audio via ConnectionManager."""
        if self.websocket:
            await conn_manager.send_bytes(data, self.websocket)

manager = ChatManager()