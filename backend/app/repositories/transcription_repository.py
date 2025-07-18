#!/usr/bin/env python3

import os
import subprocess
from typing import Optional
from configs.speech_config import TranscriptionConfig

class TranscriptionRepository:
    """Low-level transcription process management"""
    
    _instance = None
    _whisper_process: Optional[subprocess.Popen] = None
    
    def __new__(cls, config: TranscriptionConfig):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.config = config
        return cls._instance
    
    def get_whisper_process(self) -> subprocess.Popen:
        """Get or create the singleton Whisper process"""
        if not self._whisper_process or self._whisper_process.poll() is not None:
            # Process is dead or doesn't exist, create a new one
            if self._whisper_process:
                print("🔄 Whisper process died, creating new one...")
                # Check if there's any stderr output for debugging
                try:
                    stderr_output = self._whisper_process.stderr.read()
                    if stderr_output:
                        print(f"🔍 Process stderr: {stderr_output.decode('utf-8', errors='ignore')}")
                except:
                    pass
            self._whisper_process = self._start_whisper_process()
        return self._whisper_process
    
    def _start_whisper_process(self) -> subprocess.Popen:
        """Start the Rust speech recognition subprocess"""
        # Use the compiled binary instead of cargo run
        binary_path = f"{self.config.workspace_root}/whispercpp/app/target/debug/automation"
        
        # Fallback to cargo run if binary doesn't exist
        if not os.path.exists(binary_path):
            print("⚠️  Compiled binary not found, building with cargo...")
            cmd = [
                "cargo",
                "run",
                "--manifest-path",
                f"{self.config.workspace_root}/whispercpp/app/Cargo.toml",
                "--",
                "--source",
                "stdin",
                "--sample-rate",
                str(self.config.sample_rate),
            ]
        else:
            cmd = [
                binary_path,
                "--source",
                "stdin",
                "--sample-rate",
                str(self.config.sample_rate),
            ]

        try:
            process = subprocess.Popen(
                cmd,
                cwd=self.config.workspace_root,
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
                stderr=subprocess.PIPE,  # Capture stderr for debugging
                text=False,
                bufsize=0,
            )
            return process
        except Exception as e:
            print(f"❌ Failed to start speech recognition: {e}")
            raise
    
    def write_audio(self, audio_data: bytes) -> None:
        """Write audio data to the Whisper process"""
        process = self.get_whisper_process()
        try:
            process.stdin.write(audio_data)
            process.stdin.flush()
        except Exception as e:
            print(f"❌ Error writing audio to Whisper: {e}")
            # If we get a broken pipe, restart the process
            if "Broken pipe" in str(e) or "Errno 32" in str(e):
                print("🔄 Restarting Whisper process due to broken pipe...")
                self._restart_whisper_process()
                # Try writing again to the new process
                try:
                    new_process = self.get_whisper_process()
                    new_process.stdin.write(audio_data)
                    new_process.stdin.flush()
                except Exception as e2:
                    print(f"❌ Failed to write to restarted process: {e2}")
    
    def read_transcription(self) -> Optional[str]:
        """Read transcription from the Whisper process"""
        process = self.get_whisper_process()
        if process.stdout:
            try:
                # Check if there's data available without blocking
                import select
                ready, _, _ = select.select([process.stdout], [], [], 0.1)
                if not ready:
                    return None  # No data available
                
                raw = process.stdout.readline()
                if raw:
                    transcription = raw.decode("utf-8", errors="ignore").strip()
                    return transcription
            except Exception as e:
                # Only log non-broken pipe errors to reduce spam
                if "Broken pipe" not in str(e) and "Errno 32" not in str(e):
                    print(f"❌ Error reading transcription: {e}")
        return None
    
    def _restart_whisper_process(self) -> None:
        """Restart the Whisper process"""
        if self._whisper_process:
            try:
                self._whisper_process.terminate()
                self._whisper_process.wait(timeout=5)
            except:
                pass
            self._whisper_process = None
        
        # Create a new process
        self._whisper_process = self._start_whisper_process()
    
    def cleanup(self) -> None:
        """Clean up the Whisper process"""
        if self._whisper_process:
            self._whisper_process.terminate()
            self._whisper_process = None 