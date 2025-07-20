from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
from features.chat.managers.chat_manager import manager as chat_manager

router = APIRouter()

@router.websocket("/ws/chat")
async def websocket_endpoint(ws: WebSocket):
    await chat_manager.connect(ws)
    try:
        while True:
            msg = await ws.receive()
            if 'bytes' in msg:
                await chat_manager.append_audio(msg['bytes'])
            elif 'text' in msg:
                try:
                    obj = json.loads(msg['text'])
                    if obj.get('event') == 'stop':
                        await chat_manager.handle_stop()
                except json.JSONDecodeError:
                    pass
    except WebSocketDisconnect:
        await chat_manager.disconnect()