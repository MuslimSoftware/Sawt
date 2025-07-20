#!/usr/bin/env python3

from dataclasses import dataclass

@dataclass
class TranscriptionConfig:
    """Configuration for speech transcription"""
    workspace_root: str
    sample_rate: int = 16000
    model_path: str = "models/ggml-base.en.bin"

@dataclass
class TTSConfig:
    """Configuration for text-to-speech"""
    voice: str = "alloy"
    api_key: str = "" 