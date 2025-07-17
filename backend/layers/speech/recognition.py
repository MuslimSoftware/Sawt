#!/usr/bin/env python3

import subprocess
import os
import time
from typing import Generator, Optional
from dataclasses import dataclass

@dataclass
class RecognitionConfig:
    workspace_root: str
    websocket_port: int = 8765
    pcm_sample_rate: int = 16000

class SpeechRecognitionService:
    """Service for managing speech recognition via Rust whisper process"""
    
    def __init__(self, config: RecognitionConfig):
        self.config = config
        self.process: Optional[subprocess.Popen] = None
        self._model_preloaded = False
        
    def _preload_model(self) -> None:
        """Preload the Whisper model to avoid first-call latency"""
        if self._model_preloaded:
            return
            
        print("🔄 Preloading Whisper model...")
        start_time = time.time()
        
        # Create a minimal audio sample (silence) to trigger model loading
        sample_rate = self.config.pcm_sample_rate
        duration_ms = 100  # 100ms of silence
        num_samples = int(sample_rate * duration_ms / 1000)
        
        # Generate silence audio (all zeros)
        silence_audio = b'\x00\x00' * num_samples  # 16-bit PCM, little-endian
        
        try:
            # Start the Rust process
            cmd = [
                "cargo",
                "run",
                "--manifest-path",
                f"{self.config.workspace_root}/backend/hardware/app/Cargo.toml",
                "--",
                "--source",
                "stdin",
                "--sample-rate",
                str(self.config.pcm_sample_rate),
            ]
            
            temp_process = subprocess.Popen(
                cmd,
                cwd=self.config.workspace_root,
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=False,
                bufsize=0,
            )
            
            # Send silence audio to trigger model loading
            temp_process.stdin.write(silence_audio)
            temp_process.stdin.flush()
            
            # Wait a bit for model loading, then terminate
            time.sleep(2)  # Give time for model to load
            temp_process.terminate()
            temp_process.wait(timeout=5)
            
            load_time = time.time() - start_time
            print(f"✅ Whisper model preloaded in {load_time:.2f}s")
            self._model_preloaded = True
            
        except Exception as e:
            print(f"⚠️  Model preloading failed (will load on first use): {e}")
            # Don't fail the service, just continue without preloading
        
    def start_recognition(self) -> subprocess.Popen:
        """Start the Rust speech recognition subprocess (stdin mode)."""
        # Preload model before starting the main process
        self._preload_model()
        
        # Build command to run Rust binary via cargo
        cmd = [
            "cargo",
            "run",
            "--manifest-path",
            f"{self.config.workspace_root}/backend/hardware/app/Cargo.toml",
            "--",
            "--source",
            "stdin",
            "--sample-rate",
            str(self.config.pcm_sample_rate),
        ]

        try:
            self.process = subprocess.Popen(
                cmd,
                cwd=self.config.workspace_root,
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=False,
                bufsize=0,
            )

            print(f"🛰️  Rust speech recognition process started")
            return self.process
        except Exception as e:
            print(f"❌ Failed to start speech recognition: {e}")
            raise

    def get_transcription_stream(self) -> Generator[str, None, None]:
        """Yield transcribed lines from Rust process stdout."""
        if not self.process or not self.process.stdout:
            return
            
        try:
            for raw in iter(self.process.stdout.readline, b""):
                if not raw:
                    break
                line = raw.decode("utf-8", errors="ignore").strip()
                if line:
                    yield line
        except Exception as e:
            print(f"❌ Speech recognition stream error: {e}")
        finally:
            if self.process:
                self.process.terminate()
                
    def get_stdin(self):
        """Get the stdin pipe for writing audio data to Rust process."""
        return self.process.stdin if self.process else None
        
    def stop(self):
        """Stop the recognition service"""
        if self.process:
            self.process.terminate()
            self.process = None 