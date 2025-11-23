from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
from features.chat.services.chat_service import ChatService
from infrastructure.network.connection_manager import manager as conn_manager
from features.common.types.exceptions import BaseSawtException
import logging

logger = logging.getLogger(__name__)

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
                except json.JSONDecodeError as e:
                    raise BaseSawtException(
                        code="WEBSOCKET_ERROR",
                        message=f"Invalid JSON: {e}",
                        status_code=400,
                    )
    except WebSocketDisconnect as e:
        logger.info(f"Client disconnected: {e}")
        conn_manager.disconnect(ws)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        conn_manager.disconnect(ws)
       