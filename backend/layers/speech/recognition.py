#!/usr/bin/env python3

import subprocess
import os
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
        
    def start_recognition(self) -> subprocess.Popen:
        """Start the Rust speech recognition subprocess (stdin mode)."""
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