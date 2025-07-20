#!/usr/bin/env python3

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import traceback
import signal
import atexit
import os

# Import our WebSocket handler and service
from app.websocket_handler import handle_websocket
from app.services.voice_assistant_service import VoiceAssistantService
from app.repositories.agent_repository import AgentRepository
from configs.ai_config import AIConfig
from configs.settings import Settings

# Create FastAPI app
app = FastAPI(
    title="Sawt Voice Assistant",
    description="A voice assistant with speech recognition and AI capabilities",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    print(f"❌ Global exception caught: {exc}")
    print("Full traceback:")
    traceback.print_exc()
    raise exc

def cleanup_services():
    """Clean up all services when the server shuts down"""
    try:
        voice_service = VoiceAssistantService()
        voice_service.cleanup()
    except Exception as e:
        print(f"Error during service cleanup: {e}")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    cleanup_services()
    os._exit(0)

# Initialize DSPy at server startup
def initialize_services():
    """Initialize all services at server startup"""
    try:
        settings = Settings()
        ai_config = AIConfig(
            model=settings.ai_model,
            api_key=settings.ai_api_key,
            temperature=settings.ai_temperature,
            max_tokens=settings.ai_max_tokens,
            max_history=settings.max_conversation_history
        )
        AgentRepository.configure_dspy_globally(ai_config)
        print("✅ All services initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize services: {e}")
        raise

# Initialize services at startup
initialize_services()
print("🚀 Sawt Voice Assistant server ready!")

# Register cleanup functions
atexit.register(cleanup_services)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

@app.get("/")
async def root():
    """Root endpoint"""
    try:
        return {
            "message": "Sawt Voice Assistant",
            "version": "1.0.0",
            "status": "running"
        }
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
        print("Full traceback:")
        traceback.print_exc()
        raise

# Track active connections to prevent duplicates
_active_connections = set()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    client_id = None
    try:
        await websocket.accept()

        # Get client identifier (IP + user agent)
        client_host = websocket.client.host if websocket.client else "unknown"
        client_id = f"{client_host}"
        
        # Check if this client already has an active connection
        if client_id in _active_connections:
            await websocket.close(code=1008, reason="Duplicate connection")
            return
        
        _active_connections.add(client_id)
        
        await handle_websocket(websocket)
        
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        print("Full traceback:")
        traceback.print_exc()
    finally:
        # Clean up connection tracking
        if client_id and client_id in _active_connections:
            _active_connections.remove(client_id)

if __name__ == "__main__":
    print("Starting server")
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["."],
        log_level="info"
    ) 