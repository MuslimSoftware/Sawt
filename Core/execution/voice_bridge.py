#!/usr/bin/env python3

import subprocess
import sys
import os

def main():
    # Run cargo from workspace root so model path resolves correctly
    workspace_root = "/Users/younesbenketira/Code/personal/Sawt"
    
    try:
        # Run cargo run and capture output
        process = subprocess.Popen(
            ["cargo", "run", "--manifest-path", "Core/input/app/Cargo.toml"],
            cwd=workspace_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,  # Discard stderr
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Print each line of output as it comes
        for line in process.stdout:
            speechAsText = line.strip()
            if speechAsText:  # Only print non-empty lines
                print(f"\n🎤 SPEECH: {speechAsText}\n")
            
    except KeyboardInterrupt:
        print("\nStopping voice processing...")
        process.terminate()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 