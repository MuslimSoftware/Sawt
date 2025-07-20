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
    
    # Audio buffering
    _audio_buffer = bytearray()
    _min_audio_bytes = 32000  # ~2 seconds of 16kHz 16-bit audio
    _max_audio_bytes = 160000  # ~10 seconds of audio
    _last_process_time = 0
    _silence_threshold = 2.0  # Process after 2 seconds of silence
    
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
                # Get audio data from queue
                audio_data = self._audio_queue.get(timeout=0.1)
                if audio_data is None:  # Stop signal
                    break
                
                # Add to buffer
                self._audio_buffer.extend(audio_data)
                current_time = time.time()
                
                # Check if we should process the buffer
                should_process = (
                    len(self._audio_buffer) >= self._min_audio_bytes or
                    (len(self._audio_buffer) > 0 and 
                     current_time - self._last_process_time > self._silence_threshold)
                )
                
                if should_process and len(self._audio_buffer) > 0:
                    print(f"Processing audio buffer: {len(self._audio_buffer)} bytes")
                    
                    # Process the buffered audio
                    transcription = self._transcribe_audio_chunk(bytes(self._audio_buffer))
                    if transcription:
                        self._transcription_queue.put(transcription)
                    
                    # Clear buffer and update time
                    self._audio_buffer.clear()
                    self._last_process_time = current_time
                    
            except queue.Empty:
                # Check if we should process remaining buffer after silence
                current_time = time.time()
                if (len(self._audio_buffer) > 0 and 
                    current_time - self._last_process_time > self._silence_threshold):
                    
                    print(f"Processing remaining audio buffer: {len(self._audio_buffer)} bytes")
                    transcription = self._transcribe_audio_chunk(bytes(self._audio_buffer))
                    if transcription:
                        self._transcription_queue.put(transcription)
                    
                    self._audio_buffer.clear()
                    self._last_process_time = current_time
                    
                continue
            except Exception as e:
                print(f"❌ Error in audio processing loop: {e}")
    
    def _transcribe_audio_chunk(self, audio_data: bytes) -> Optional[str]:
        """Transcribe a chunk of audio data using the Rust binary"""
        try:
            if len(audio_data) < 1000:  # Skip very small chunks
                return None
                
            print(f"Transcribing audio chunk: {len(audio_data)} bytes")
            
            # Run the Rust binary with the audio data
            cmd = [
                "/app/automation",
                "--stdin"
            ]
            
            # Execute the command and capture output
            result = subprocess.run(
                cmd,
                input=audio_data,
                capture_output=True,
                text=False,  # Handle binary data
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout.strip():
                transcription = result.stdout.decode('utf-8').strip()
                if transcription and len(transcription.strip()) > 2:
                    return transcription
                else:
                    print("Transcription too short or empty, skipping")
                    return None
            else:
                error_msg = result.stderr.decode('utf-8') if result.stderr else "Unknown error"
                print(f"❌ Transcription failed: {error_msg}")
                return None
            
        except subprocess.TimeoutExpired:
            print("❌ Transcription timed out")
            return None
        except Exception as e:
            print(f"❌ Error transcribing audio chunk: {e}")
            return None
    
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