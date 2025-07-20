from fastapi import WebSocket
from typing import List

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_text(self, message: str, websocket: WebSocket):
        """Send text to one connection."""
        await websocket.send_text(message)

    async def send_bytes(self, data: bytes, websocket: WebSocket):
        """Send binary data to one connection."""
        await websocket.send_bytes(data)

    async def send_json(self, data, websocket: WebSocket):
        """Send JSON data to one connection."""
        await websocket.send_json(data)

manager = ConnectionManager()
