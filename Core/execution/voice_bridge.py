#!/usr/bin/env python3

import subprocess
import os
import dspy
import edge_tts
import io
import soundfile as sf
import sounddevice as sd
import asyncio
from gtts import gTTS

print("Initializing DSPy...")
lm = dspy.LM(
    model="gemini/gemini-2.0-flash-exp", 
    api_key=os.getenv("GEMINI_API_KEY"),
    max_tokens=4000,
    temperature=0.1
)
print("✅ DSPy ready!")

dspy.configure(lm=lm)

# en-US-ChristopherNeural
# en-US-EricNeural
# en-US-GuyNeural
# en-US-RogerNeural
# en-US-SteffanNeural
async def speak(text, voice="en-US-ChristopherNeural"):
    communicate = edge_tts.Communicate(text, voice=voice)
    audio_bytes = bytearray()
    
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_bytes.extend(chunk["data"])
    
    buffer = io.BytesIO(audio_bytes)
    data, samplerate = sf.read(buffer, dtype="float32")
    sd.play(data, samplerate)
    sd.wait()

async def main():
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

                await speak(result.output)

    except KeyboardInterrupt:
        print("\nStopping voice processing...")
        process.terminate()

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 