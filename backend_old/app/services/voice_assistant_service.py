#!/usr/bin/env python3

from typing import Optional
from configs.settings import Settings
from configs.speech_config import TranscriptionConfig, TTSConfig
from configs.ai_config import AIConfig
from app.repositories.transcription_repository import TranscriptionRepository
from app.repositories.agent_repository import AgentRepository
from app.repositories.tts_repository import TTSRepository
from app.services.agent_service import AgentService
from app.services.tts_service import TTSService

class VoiceAssistantService:
    """Main orchestrator service for voice assistant functionality"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        # Load configurations
        settings = Settings()
        
        # Initialize repositories
        transcription_config = TranscriptionConfig(workspace_root=settings.workspace_root)
        ai_config = AIConfig(
            model=settings.ai_model,
            api_key=settings.ai_api_key,
            temperature=settings.ai_temperature,
            max_tokens=settings.ai_max_tokens,
            max_history=settings.max_conversation_history
        )
        tts_config = TTSConfig(voice=settings.default_voice)
        
        self.transcription_repo = TranscriptionRepository(transcription_config)
        self.agent_repo = AgentRepository(ai_config)
        self.tts_repo = TTSRepository(tts_config)
        
        # Initialize services
        self.agent_service = AgentService(self.agent_repo)
        self.tts_service = TTSService(self.tts_repo)
        
        self._initialized = True
    
    async def process_transcription(self, connection_id: str, transcription: str) -> tuple[Optional[str], Optional[bytes]]:
        """Process transcription through AI and TTS pipeline"""
        try:
            # Step 1: Process with AI agent
            response, is_directed_at_agent = self.agent_service.process_user_input(connection_id, transcription)
            if not is_directed_at_agent:
                return "[Not directed at agent]", None
            
            # Step 2: Synthesize response
            audio_response = await self.tts_service.synthesize_response(response)
            return response, audio_response
            
        except Exception as e:
            print(f"❌ Voice assistant transcription processing error: {e}")
            return None, None
    
    def cleanup_connection(self, connection_id: str) -> None:
        """Clean up all state for a connection"""
        self.agent_service.cleanup_connection(connection_id)
    
    def cleanup(self) -> None:
        """Clean up all resources"""
        self.transcription_repo.cleanup() 