#!/usr/bin/env python3

import queue
import threading
from typing import Optional
import httpx
import webrtcvad
from configs.speech_config import TranscriptionConfig

class TranscriptionRepository:
    """Manages audio processing with VAD and sends speech to a remote transcriber service."""
    
    _instance = None
    _audio_queue = queue.Queue()
    _transcription_queue = queue.Queue()
    _processing_thread = None
    _stop_event = threading.Event()
    
    # VAD settings
    _VAD_AGGRESSIVENESS = 3
    _VAD_FRAME_MS = 30
    _VAD_SAMPLE_RATE = 16000
    _VAD_FRAME_SAMPLES = int(_VAD_SAMPLE_RATE * (_VAD_FRAME_MS / 1000.0))
    _VAD_BYTES_PER_SAMPLE = 2
    _VAD_FRAME_BYTES = _VAD_FRAME_SAMPLES * _VAD_BYTES_PER_SAMPLE
    
    _speech_buffer = bytearray()
    _is_speaking = False
    _silence_frames_after_speech = 0
    _SILENCE_FRAMES_THRESHOLD = 50

    def __new__(cls, config: TranscriptionConfig):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.config = config
            cls._instance.vad = webrtcvad.Vad(cls._VAD_AGGRESSIVENESS)
            cls._instance.transcriber_url = "http://transcriber:3001/transcribe"
            cls._instance.http_client = httpx.Client(timeout=30.0)
            print("Starting transcription repository with VAD and HTTP client")
            cls._instance._start_processing_thread()
        return cls._instance
    
    def _start_processing_thread(self):
        if self._processing_thread is None or not self._processing_thread.is_alive():
            self._stop_event.clear()
            self._processing_thread = threading.Thread(target=self._process_audio_loop, daemon=True)
            self._processing_thread.start()
            
    def _process_audio_loop(self):
        audio_buffer = bytearray()
        while not self._stop_event.is_set():
            try:
                audio_data = self._audio_queue.get(timeout=0.1)
                if audio_data is None:
                    break
                audio_buffer.extend(audio_data)

                while len(audio_buffer) >= self._VAD_FRAME_BYTES:
                    frame = audio_buffer[:self._VAD_FRAME_BYTES]
                    audio_buffer = audio_buffer[self._VAD_FRAME_BYTES:]

                    if self.vad.is_speech(frame, self._VAD_SAMPLE_RATE):
                        self._speech_buffer.extend(frame)
                        self._is_speaking = True
                        self._silence_frames_after_speech = 0
                    elif self._is_speaking:
                        self._silence_frames_after_speech += 1
                        if self._silence_frames_after_speech > self._SILENCE_FRAMES_THRESHOLD:
                            self._finalize_speech_segment()
            except queue.Empty:
                if self._is_speaking and self._silence_frames_after_speech > self._SILENCE_FRAMES_THRESHOLD:
                    self._finalize_speech_segment()
                continue
            except Exception as e:
                print(f"❌ Error in audio processing loop: {e}")

    def _finalize_speech_segment(self):
        if len(self._speech_buffer) > self._VAD_FRAME_BYTES * 5:
            print(f"Processing speech segment: {len(self._speech_buffer)} bytes")
            transcription = self._transcribe_audio_chunk(bytes(self._speech_buffer))
            if transcription:
                self._transcription_queue.put(transcription)
        
        self._speech_buffer.clear()
        self._is_speaking = False
        self._silence_frames_after_speech = 0

    def _transcribe_audio_chunk(self, audio: bytes) -> Optional[str]:
        try:
            response = self.http_client.post(self.transcriber_url, content=audio)
            response.raise_for_status()
            data = response.json()
            return data.get("transcription")
        except httpx.RequestError as e:
            print(f"❌ HTTP request to transcriber failed: {e}")
            return None
        except httpx.HTTPStatusError as e:
            print(f"❌ Transcriber service returned an error: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            print(f"❌ Error transcribing audio chunk: {e}")
            return None
    
    def write_audio(self, audio_data: bytes) -> None:
        self._audio_queue.put(audio_data)
    
    def read_transcription(self) -> Optional[str]:
        try:
            return self._transcription_queue.get_nowait()
        except queue.Empty:
            return None
    
    def cleanup(self) -> None:
        print("Cleaning up transcription repository")
        self._stop_event.set()
        self._audio_queue.put(None)
        if self._processing_thread and self._processing_thread.is_alive():
            self._processing_thread.join(timeout=2.0)
        self.http_client.close()
 