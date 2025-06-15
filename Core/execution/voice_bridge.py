#!/usr/bin/env python3

import subprocess
import sys
import os
import warnings
import dspy
from TTS.api import TTS
import numpy
import simpleaudio as sa

print("Initializing DSPy...")
lm = dspy.LM(
    model="gemini/gemini-2.0-flash-exp", 
    api_key=os.getenv("GEMINI_API_KEY"),
    max_tokens=4000,
    temperature=0.1
)
print("✅ DSPy ready!")

dspy.configure(lm=lm)

print("Initializing TTS model...")
print(TTS().list_models())
tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)
print("✅ TTS model ready!")

def main():
    print("Starting voice processing...")
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
                print(f"\n🎤 SPEECH: {speechAsText}")
                
                agent = dspy.Predict('input -> output')
                result = agent(input=speechAsText)
                print("🎧 AI says:", result.output)

                # Generate audio waveform as a NumPy array and sample rate
                wav = tts.tts(result.output)
                
                # Convert float32 audio to int16 for simpleaudio
                # TTS outputs float32 in range [-1, 1], convert to int16 range [-32768, 32767]
                if isinstance(wav, list):
                    wav = np.array(wav)
                wav = np.clip(wav, -1.0, 1.0)  # Ensure values are in valid range
                wav_int16 = (wav * 32767).astype(np.int16)

                # Play audio using simpleaudio
                # Parameters: audio_data, num_channels, bytes_per_sample, sample_rate
                play_obj = sa.play_buffer(wav_int16.tobytes(), 1, 2, 22050)
                print("🔊 Playing audio...")
                play_obj.wait_done()
                print("✅ Audio finished")

    except KeyboardInterrupt:
        print("\nStopping voice processing...")
        process.terminate()

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 