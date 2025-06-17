#!/usr/bin/env python3

import subprocess
import os

WORKSPACE_ROOT = "/Users/younesbenketira/Code/personal/Sawt"

def start_speech_recognition():
    """Start the speech recognition subprocess"""
    try:
        process = subprocess.Popen(
            ["cargo", "run", "--manifest-path", "Core/input/app/Cargo.toml"],
            cwd=WORKSPACE_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        return process
    except Exception as e:
        print(f"❌ Failed to start speech recognition: {e}")
        raise

def get_speech_text_stream(process):
    """Generator that yields speech text from the recognition process"""
    try:
        for line in process.stdout:
            speech_text = line.strip()
            if speech_text:
                yield speech_text
    except Exception as e:
        print(f"❌ Speech recognition stream error: {e}")
    finally:
        if process:
            process.terminate() 