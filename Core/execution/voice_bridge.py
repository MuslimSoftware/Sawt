#!/usr/bin/env python3

import asyncio
from agent import AIAgent
import text_to_speech
import speech_to_text

async def main():
    """Main function with speech processing loop"""
    print("Starting voice processing...")
    
    # Initialize AI agent
    agent = AIAgent()
    
    # Start speech recognition
    process = None
    try:
        process = speech_to_text.start_speech_recognition()
        
        # Process each line of speech input
        for speech_text in speech_to_text.get_speech_text_stream(process):
            
            # Generate AI response
            ai_response = agent.generate_response(speech_text)

            print(f"\n🎤 SPEECH: {speech_text}")
            print(f"🎧 AI says: {ai_response}")
            
            # Convert to speech and play
            await text_to_speech.speak(ai_response)
            
    except KeyboardInterrupt:
        print("\nStopping voice processing...")
    except Exception as e:
        print(f"❌ Voice processing error: {e}")
    finally:
        if process:
            process.terminate()

if __name__ == "__main__":
    asyncio.run(main()) 