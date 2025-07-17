#!/usr/bin/env python3

import asyncio
from typing import Optional
from .recognition import SpeechRecognitionService, RecognitionConfig
from .synthesis import TextToSpeechService
from ..ai.agent import AIAgent
from ..communication.websocket_manager import WebSocketManager, WebSocketConfig

class VoiceProcessingPipeline:
    """Orchestrates the complete voice processing pipeline"""
    
    def __init__(self, 
                 recognition: SpeechRecognitionService,
                 synthesis: TextToSpeechService,
                 agent: AIAgent,
                 websocket: WebSocketManager):
        self.recognition = recognition
        self.synthesis = synthesis
        self.agent = agent
        self.websocket = websocket
        self._running = False
        
    async def process_speech_input(self, speech_text: str) -> None:
        """Process a single speech input through the complete pipeline"""
        print(f"\n🎤 SPEECH: {speech_text}")
        
        # Send user transcript immediately
        self.websocket.broadcast_text("user", speech_text)

        # Classify if user is directing at agent
        is_directed_at_agent, reasoning = self.agent.classify_intent(speech_text)
        
        if not is_directed_at_agent:
            print(f"👤 User is not directing at the agent: {reasoning}")
            self.websocket.broadcast_text("ai", "[Ignored since not directed at agent]")
            return
        else:
            print(f"👤 User is directing at the agent: {reasoning}")

        # Send stop signal to interrupt any ongoing AI audio at clients
        self.websocket.broadcast_control("stop_audio")

        # Generate AI response
        ai_response = self.agent.generate_response(speech_text)
        print(f"🎧 AI says: {ai_response}")

        # Send AI transcript
        self.websocket.broadcast_text("ai", ai_response)

        # Generate TTS audio and stream it
        try:
            audio_bytes = await self.synthesis.synthesize_bytes(ai_response)
            self.websocket.broadcast_audio(audio_bytes)
        except Exception as e:
            print(f"❌ TTS synthesis failed: {e}")
            self.websocket.broadcast_text("ai", "[TTS Error]")
            
    async def run_continuous_processing(self) -> None:
        """Run the continuous speech processing pipeline"""
        print("Starting voice processing...")
        
        try:
            self._running = True
            # Process speech transcriptions
            for speech_text in self.recognition.get_transcription_stream():
                if not self._running:
                    break
                    
                await self.process_speech_input(speech_text)
                
        except KeyboardInterrupt:
            print("\nStopping voice processing...")
        except Exception as e:
            print(f"❌ Voice processing error: {e}")
        finally:
            self._running = False
                
    def stop(self) -> None:
        """Stop the processing pipeline"""
        self._running = False
        self.recognition.stop()
        
    def is_running(self) -> bool:
        """Check if the pipeline is running"""
        return self._running
        
    def get_status(self) -> dict:
        """Get the current status of the pipeline"""
        return {
            "running": self._running,
            "websocket_clients": self.websocket.get_clients_count(),
            "ai_history_length": self.agent.get_history_length(),
            "websocket_running": self.websocket.is_running()
        } 