#!/usr/bin/env python3

import asyncio
from agent import AIAgent
import text_to_speech
import speech_to_text
import threading, websockets
import json
from speech_to_text import WEBSOCKET_PORT as AUDIO_WS_PORT  # 8765

# reuse speech_to_text's WebSocket server clients & loop
# they are populated inside speech_to_text._start_ws_server

def _ensure_loop():
    loop = getattr(speech_to_text, "WS_LOOP", None)
    if loop is None:
        print("🛑 WebSocket loop not ready")
    return loop

def _clients():
    return getattr(speech_to_text, "CLIENTS", set())

def broadcast_text(role: str, text: str):
    loop = _ensure_loop()
    if not _clients() or loop is None:
        return

    payload = json.dumps({"type": "text", "role": role, "text": text})

    async def _send():
        for ws in list(_clients()):
            try:
                await ws.send(payload)
            except Exception:
                _clients().discard(ws)

    asyncio.run_coroutine_threadsafe(_send(), loop)

def broadcast_audio(data: bytes):
    loop = _ensure_loop()
    if not _clients() or loop is None:
        return

    async def _send():
        for ws in list(_clients()):
            try:
                await ws.send(data)
            except Exception:
                _clients().discard(ws)

    asyncio.run_coroutine_threadsafe(_send(), loop)

def broadcast_control(cmd: str):
    loop = _ensure_loop()
    if not _clients() or loop is None:
        return

    payload = json.dumps({"type": "control", "command": cmd})

    async def _send():
        for ws in list(_clients()):
            try:
                await ws.send(payload)
            except Exception:
                _clients().discard(ws)

    asyncio.run_coroutine_threadsafe(_send(), loop)

async def main():
    print("Starting voice processing...")

    agent = AIAgent()
    process = None
    try:
        process = speech_to_text.start_speech_recognition()
        
        for speech_text in speech_to_text.get_speech_text_stream(process):
            # send stop signal to interrupt any ongoing AI audio at clients
            broadcast_control("stop_audio")

            # send user transcript immediately
            broadcast_text("user", speech_text)

            print(f"\n🎤 SPEECH: {speech_text}")

            # generate AI response
            ai_response = agent.generate_response(speech_text)
            print(f"🎧 AI says: {ai_response}")

            # send AI transcript
            broadcast_text("ai", ai_response)

            # Generate TTS audio and stream it
            audio_bytes = await text_to_speech.synthesize_bytes(ai_response)
            broadcast_audio(audio_bytes)
            
    except KeyboardInterrupt:
        print("\nStopping voice processing...")
    except Exception as e:
        print(f"❌ Voice processing error: {e}")
    finally:
        if process:
            process.terminate()

if __name__ == "__main__":
    asyncio.run(main()) 