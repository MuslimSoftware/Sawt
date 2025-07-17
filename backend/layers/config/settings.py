#!/usr/bin/env python3

import os
from typing import Optional
from dataclasses import dataclass

@dataclass
class Settings:
    """Application settings with environment variable support"""
    
    # Workspace and paths
    workspace_root: str = "/Users/younesbenketira/Code/personal/Sawt"
    
    # WebSocket configuration
    websocket_host: str = "0.0.0.0"
    websocket_port: int = 8765
    
    # Audio processing
    pcm_sample_rate: int = 16000
    
    # AI configuration
    ai_model: Optional[str] = None
    ai_api_key: Optional[str] = None
    max_conversation_history: int = 20
    ai_temperature: float = 0.1
    ai_max_tokens: int = 4000
    
    # TTS configuration
    default_voice: str = "en-US-ChristopherNeural"
    
    def __post_init__(self):
        """Load values from environment variables after initialization"""
        # Load from environment variables if not explicitly set
        self.workspace_root = os.getenv("WORKSPACE_ROOT", self.workspace_root)
        self.websocket_host = os.getenv("WEBSOCKET_HOST", self.websocket_host)
        self.websocket_port = int(os.getenv("WEBSOCKET_PORT", str(self.websocket_port)))
        self.pcm_sample_rate = int(os.getenv("PCM_SAMPLE_RATE", str(self.pcm_sample_rate)))
        
        # AI settings
        self.ai_model = self.ai_model or os.getenv("AI_MODEL")
        self.ai_api_key = self.ai_api_key or os.getenv("AI_API_KEY")
        self.max_conversation_history = int(os.getenv("MAX_CONVERSATION_HISTORY", str(self.max_conversation_history)))
        self.ai_temperature = float(os.getenv("AI_TEMPERATURE", str(self.ai_temperature)))
        self.ai_max_tokens = int(os.getenv("AI_MAX_TOKENS", str(self.ai_max_tokens)))
        
        # TTS settings
        self.default_voice = os.getenv("DEFAULT_VOICE", self.default_voice)
        
    def validate(self) -> list[str]:
        """Validate required settings and return list of errors"""
        errors = []
        
        # Check required AI settings
        if not self.ai_model:
            errors.append("AI_MODEL environment variable is required")
        if not self.ai_api_key:
            errors.append("AI_API_KEY environment variable is required")
            
        # Check workspace exists
        if not os.path.exists(self.workspace_root):
            errors.append(f"Workspace root does not exist: {self.workspace_root}")
            
        # Check port range
        if not (1024 <= self.websocket_port <= 65535):
            errors.append(f"WebSocket port must be between 1024 and 65535, got: {self.websocket_port}")
            
        return errors
        
    def get_websocket_url(self) -> str:
        """Get the WebSocket URL for clients"""
        return f"ws://{self.websocket_host}:{self.websocket_port}"
        
    def get_rust_manifest_path(self) -> str:
        """Get the path to the Rust Cargo.toml file"""
        return f"{self.workspace_root}/backend/hardware/app/Cargo.toml"
        
    def to_dict(self) -> dict:
        """Convert settings to dictionary (excluding sensitive data)"""
        return {
            "workspace_root": self.workspace_root,
            "websocket_host": self.websocket_host,
            "websocket_port": self.websocket_port,
            "pcm_sample_rate": self.pcm_sample_rate,
            "ai_model": self.ai_model,
            "max_conversation_history": self.max_conversation_history,
            "ai_temperature": self.ai_temperature,
            "ai_max_tokens": self.ai_max_tokens,
            "default_voice": self.default_voice,
        } 