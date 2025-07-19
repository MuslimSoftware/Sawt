#!/usr/bin/env python3

import os
import subprocess
import threading
import queue
import time
from typing import Optional
from configs.speech_config import TranscriptionConfig

class TranscriptionRepository:
    """Low-level transcription process management"""
    
    _instance = None
    _audio_queue = queue.Queue()
    _transcription_queue = queue.Queue()
    _processing_thread = None
    _stop_event = threading.Event()
    
    def __new__(cls, config: TranscriptionConfig):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.config = config
            print("starting transcription repository")
            cls._instance._start_processing_thread()
        return cls._instance
    
    def _start_processing_thread(self):
        """Start the background processing thread"""
        if self._processing_thread is None or not self._processing_thread.is_alive():
            self._stop_event.clear()
            self._processing_thread = threading.Thread(target=self._process_audio_loop, daemon=True)
            self._processing_thread.start()
    
    def _process_audio_loop(self):
        """Background thread that processes audio and generates transcriptions"""
        while not self._stop_event.is_set():
            try:
                print("Processing audio chunk")
                # Get audio data from queue
                audio_data = self._audio_queue.get(timeout=1.0)
                if audio_data is None:  # Stop signal
                    break
                
                # Process audio data using the Rust binary
                transcription = self._transcribe_audio_chunk(audio_data)
                if transcription:
                    self._transcription_queue.put(transcription)
                    
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ Error in audio processing loop: {e}")
    
    def _transcribe_audio_chunk(self, audio_data: bytes) -> Optional[str]:
        """Transcribe a chunk of audio data using the Rust binary"""
        try:
            print(f"Transcribing audio chunk: {len(audio_data)} bytes")
                
            # Create a temporary audio file
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            # Run the Rust binary with the audio file
            cmd = [
                "/app/automation",
                "--model", "/app/models/ggml-base.en.bin",
                "--stdin"
            ]
            
            # Execute the command and capture output
            result = subprocess.run(
                cmd,
                input=audio_data,
                capture_output=True,
                text=False,  # Changed from text=True to handle binary data
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.decode('utf-8').strip()  # Decode bytes to string
            else:
                print(f"❌ Transcription failed: {result.stderr.decode('utf-8')}")
                return None
            
        except subprocess.TimeoutExpired:
            print("❌ Transcription timed out")
            return None
        except Exception as e:
            print(f"❌ Error transcribing audio chunk: {e}")
            return None
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except:
                pass
    
    def write_audio(self, audio_data: bytes) -> None:
        """Write audio data to the processing queue"""
        try:
            self._audio_queue.put(audio_data)
        except Exception as e:
            print(f"❌ Error writing audio to queue: {e}")
    
    def read_transcription(self) -> Optional[str]:
        """Read transcription from the queue"""
        try:
            return self._transcription_queue.get_nowait()
        except queue.Empty:
            return None
    
    def cleanup(self) -> None:
        """Clean up the processing thread"""
        self._stop_event.set()
        self._audio_queue.put(None)  # Stop signal
        if self._processing_thread and self._processing_thread.is_alive():
            self._processing_thread.join(timeout=5.0) 