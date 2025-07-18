#!/usr/bin/env python3

import json
import uuid
import asyncio
import traceback
from fastapi import WebSocket
from app.services.voice_assistant_service import VoiceAssistantService

async def handle_websocket(websocket: WebSocket):
    """Handle WebSocket connection with stateless design"""
    connection_id = str(uuid.uuid4())
    voice_service = VoiceAssistantService()
    
    print(f"🔗 WebSocket connection opened: {connection_id}")
    
    transcription_task = asyncio.create_task(read_transcriptions(websocket, voice_service, connection_id))
    
    try:
        while True:
            # Receive audio data
            audio_data = await websocket.receive_bytes()
            
            voice_service.transcription_repo.write_audio(audio_data)
                
    except Exception as e:
        # Handle WebSocket disconnect gracefully
        if "WebSocketDisconnect" in str(type(e)):
            print(f"🔌 WebSocket disconnected normally: {connection_id}")
            voice_service.cleanup_connection(connection_id)
        else:
            print(f"❌ WebSocket handler error: {e}")
            traceback.print_exc()
            voice_service.cleanup_connection(connection_id)
    finally:
        # Cancel the transcription task
        print(f"🧹 Cleaning up connection: {connection_id}")
        transcription_task.cancel()
        try:
            await transcription_task
        except asyncio.CancelledError:
            pass

async def read_transcriptions(websocket: WebSocket, voice_service, connection_id: str):
    """Background task to continuously read transcriptions"""
    try:
        while True:
            # Read transcription from the repository
            loop = asyncio.get_event_loop()
            transcription = await loop.run_in_executor(None, voice_service.transcription_repo.read_transcription)
            
            if transcription and len(transcription.strip()) > 2:
                # Send user transcription as text message
                user_message = {
                    "type": "text",
                    "role": "user",
                    "text": transcription.strip()
                }
                await websocket.send_text(json.dumps(user_message))
                
                # Process the transcription through the voice assistant
                response_text, response_audio = await voice_service.process_transcription(connection_id, transcription.strip())
                
                # Send agent response as text message if available
                if response_text:
                    agent_message = {
                        "type": "text",
                        "role": "ai",
                        "text": response_text
                    }
                    await websocket.send_text(json.dumps(agent_message))
                
                # Send audio response if available
                if response_audio:
                    # Send stop_audio command to prevent multiple audio streams
                    stop_audio_message = {
                        "type": "control",
                        "command": "stop_audio"
                    }
                    await websocket.send_text(json.dumps(stop_audio_message))
                    
                    # Send the new audio
                    await websocket.send_bytes(response_audio)
            
            # Small delay to prevent busy waiting
            await asyncio.sleep(0.01)
            
    except asyncio.CancelledError:
        # Task was cancelled, exit gracefully
        pass
    except Exception as e:
        print(f"❌ Transcription reading error: {e}")
        traceback.print_exc() 