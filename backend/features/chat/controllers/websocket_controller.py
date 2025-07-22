from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
from features.chat.services.chat_service import ChatService
from infrastructure.network.connection_manager import manager as conn_manager
from features.common.types.exceptions import BaseSawtException

router = APIRouter()

@router.websocket("/ws/chat")
async def websocket_endpoint(ws: WebSocket):
    await conn_manager.connect(ws)
    chat_service = ChatService(ws)

    try:
        while True:
            msg = await ws.receive()
            if 'bytes' in msg:
                await chat_service.append_audio(msg['bytes'])
            elif 'text' in msg:
                try:
                    obj = json.loads(msg['text'])
                    if obj.get('event') == 'stop':
                        await chat_service.handle_stop_event()
                except json.JSONDecodeError:
                    pass  # Ignore non-JSON text messages
    except WebSocketDisconnect:
        print("Client disconnected")
        raise BaseSawtException(
            code="WEBSOCKET_CONNECTION_ERROR",
            message="Client disconnected",
            status_code=500,
        )
    except Exception as e:
        print(f"Error: {e}")
        raise BaseSawtException(
            code="WEBSOCKET_ERROR",
            message=str(e),
            status_code=500,
        )
    finally:
        conn_manager.disconnect(ws)