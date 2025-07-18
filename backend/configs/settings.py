#!/usr/bin/env python3

import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class Settings:
    """Main application settings"""
    
    # Workspace and paths
    workspace_root: str = str(Path(__file__).parent.parent)
    
    # WebSocket settings
    websocket_port: int = 8765
    
    # Audio settings
    pcm_sample_rate: int = 16000
    
    # AI settings
    ai_model: str = os.getenv("AI_MODEL", "gpt-4o-mini")
    ai_api_key: str = os.getenv("AI_API_KEY", "")
    ai_temperature: float = 0.1
    ai_max_tokens: int = 4000
    max_conversation_history: int = 20
    
    # TTS settings
    default_voice: str = "en-US-AriaNeural"
    
    def __post_init__(self):
        """Validate required settings"""
        if not self.ai_api_key:
            raise ValueError("AI_API_KEY environment variable is required") 