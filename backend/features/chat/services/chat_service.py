import asyncio
from fastapi import WebSocket
from features.speech.services.speech_service import SpeechService
from features.agent.services.agent_service import AgentService
from features.chat.services.transcription_service import TranscriptionService
from infrastructure.network.connection_manager import manager as conn_manager
import logging
from features.common.types.exceptions import ProviderException, RateLimitException

logger = logging.getLogger(__name__)

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

        logger.info(f"Handling stop event with {len(pcm_data)} chunks")

        try:
            await self.send_event("transcription_start")
            user_transcribed_speech = await TranscriptionService.transcribe_audio(pcm_data)
        except ProviderException as e:
            await self.send_text("ai", "[Error: Transcription Rate Limit Exceeded]")
            return
        except Exception as e:
            await self.send_text("ai", "[Error: Transcription Error]") 
            return
        
        logger.info(f"Transcription complete: {user_transcribed_speech}")

        try:
            await self.send_event("get_agent_response_start")
            agent_response, is_directed_at_agent = self.agent_service.get_response(user_transcribed_speech)
        except RateLimitException as e:
            await self.send_text("user", user_transcribed_speech)
            await self.send_text("ai", "[Error: Agent Model Rate Limit Exceeded]")
            return
        except ProviderException as e:
            await self.send_text("user", user_transcribed_speech)
            await self.send_text("ai", "[Error: Agent Model Provider Error]")
            return
        
        logger.info(f"Agent response: {agent_response}")
        
        if is_directed_at_agent and agent_response:
            try:
                await self.send_event("tts_start")
                audio_bytes = await self.speech_service.text_to_speech(agent_response)

                logger.info(f"Sending audio: {len(audio_bytes)} bytes")
                
                await asyncio.gather(
                    self.send_audio(audio_bytes),
                    self.send_text("user", user_transcribed_speech),
                    self.send_text("ai", agent_response)
                )
            except Exception as e:
                await self.send_text("ai", "[Error: TTS Error]")
                return
        else:
            await self.send_text("ai", "[Ignored: Not directed at agent]")

    async def send_text(self, role: str, text: str):
        """Sends a text message to the client."""
        try:
            await conn_manager.send_json({
                "type": "text",
                "role": role,
                "text": text
            }, self.websocket)
        except Exception as e:
            logger.critical(f"Websocket send text error: {str(e)}")
            return

    async def send_audio(self, data: bytes):
        """Sends binary audio data to the client."""
        try:
            await conn_manager.send_bytes(data, self.websocket)
        except Exception as e:
            logger.critical(f"Websocket send audio error: {str(e)}")
            return
        
    async def send_event(self, event: str):
        """Sends a event to the client."""
        try:
            await conn_manager.send_json({
                "type": "event",
                "event": event
            }, self.websocket)
        except Exception as e:
            logger.critical(f"Websocket send event error: {str(e)}")
            return
