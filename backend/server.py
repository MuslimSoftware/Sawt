#!/usr/bin/env python3

import asyncio
import signal
import sys
from typing import Optional
from fastapi import FastAPI, WebSocket
import uvicorn

# Import our new layered architecture
from layers.config.settings import Settings
from layers.speech.recognition import SpeechRecognitionService, RecognitionConfig
from layers.speech.synthesis import TextToSpeechService
from layers.speech.pipeline import VoiceProcessingPipeline
from layers.ai.agent import AIAgent
from layers.communication.websocket_manager import WebSocketManager, WebSocketConfig

class VoiceAssistantServer:
    """Main voice assistant server orchestrating all components"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.fastapi_app = FastAPI(title="Sawt Voice Assistant", version="1.0.0")
        self.pipeline: Optional[VoiceProcessingPipeline] = None
        self._setup_routes()
        
    def _setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.fastapi_app.get("/")
        def read_root():
            return {
                "message": "Sawt Voice Assistant",
                "version": "1.0.0",
                "websocket_url": self.settings.get_websocket_url()
            }
            
        @self.fastapi_app.get("/health")
        def health_check():
            status = self.pipeline.get_status() if self.pipeline else {"running": False}
            return {
                "status": "healthy" if status.get("running", False) else "stopped",
                "details": status
            }
            
        @self.fastapi_app.get("/config")
        def get_config():
            return self.settings.to_dict()
            
        @self.fastapi_app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            while True:
                try:
                    data = await websocket.receive_text()
                    await websocket.send_text(f"Message text was: {data}")
                except Exception:
                    break
                    
    def _initialize_components(self):
        """Initialize all the layered components"""
        print("🔧 Initializing voice assistant components...")
        
        # Validate settings
        errors = self.settings.validate()
        if errors:
            print("❌ Configuration errors:")
            for error in errors:
                print(f"  - {error}")
            sys.exit(1)
            
        # Initialize WebSocket manager
        ws_config = WebSocketConfig(
            host=self.settings.websocket_host,
            port=self.settings.websocket_port
        )
        websocket_manager = WebSocketManager(ws_config)
        
        # Initialize speech recognition
        recognition_config = RecognitionConfig(
            workspace_root=self.settings.workspace_root,
            websocket_port=self.settings.websocket_port,
            pcm_sample_rate=self.settings.pcm_sample_rate
        )
        recognition_service = SpeechRecognitionService(recognition_config)
        
        # Initialize text-to-speech
        synthesis_service = TextToSpeechService(self.settings.default_voice)
        
        # Initialize AI agent
        ai_agent = AIAgent(
            model=self.settings.ai_model,
            api_key=self.settings.ai_api_key,
            max_history=self.settings.max_conversation_history,
            temperature=self.settings.ai_temperature,
            max_tokens=self.settings.ai_max_tokens
        )
        
        # Create the processing pipeline
        self.pipeline = VoiceProcessingPipeline(
            recognition=recognition_service,
            synthesis=synthesis_service,
            agent=ai_agent,
            websocket=websocket_manager
        )
        
        print("✅ All components initialized successfully!")
        
    async def start(self):
        """Start the voice assistant server"""
        print("🚀 Starting Sawt Voice Assistant...")
        
        # Initialize components
        self._initialize_components()
        
        # Start Rust process first
        rust_process = self.pipeline.recognition.start_recognition()
        
        # Start WebSocket server with Rust stdin
        self.pipeline.websocket.start_server(rust_process.stdin)
        
        # Start voice processing pipeline
        await self.pipeline.run_continuous_processing()
        
    async def stop(self):
        """Stop the voice assistant server"""
        print("🛑 Stopping Sawt Voice Assistant...")
        if self.pipeline:
            self.pipeline.stop()
            
    def get_fastapi_app(self) -> FastAPI:
        """Get the FastAPI application instance"""
        return self.fastapi_app

def main():
    """Main entry point"""
    # Load settings
    settings = Settings()
    
    # Create server instance
    server = VoiceAssistantServer(settings)
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        print(f"\n📡 Received signal {signum}, shutting down gracefully...")
        asyncio.create_task(server.stop())
        
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run the server
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()