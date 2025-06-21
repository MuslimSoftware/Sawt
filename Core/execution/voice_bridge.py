#!/usr/bin/env python3

import asyncio
from agent import AIAgent
import text_to_speech
import speech_to_text
import threading, websockets
import json

RESPONSE_WS_PORT = 8766
_clients = set()
_response_loop = None

async def _ws_broadcast_handler(ws, *_):
    _clients.add(ws)
    try:
        await ws.wait_closed()
    finally:
        _clients.discard(ws)

def _start_response_ws_server():
    global _response_loop
    async def run():
        async with websockets.serve(_ws_broadcast_handler, "0.0.0.0", RESPONSE_WS_PORT):
            print(f"🗣️  Response WebSocket running on ws://localhost:{RESPONSE_WS_PORT}")
            await asyncio.Future()

    _response_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(_response_loop)
    _response_loop.run_until_complete(run())

def broadcast_text(role: str, text: str):
    if not _clients or _response_loop is None:
        print("No clients or response loop")
        return

    payload = json.dumps({"role": role, "text": text})

    async def _send():
        to_remove = []
        for ws in list(_clients):
            try:
                print(f"Sending {payload} to {ws}")
                await ws.send(payload)
            except Exception:
                to_remove.append(ws)
        for ws in to_remove:
            _clients.discard(ws)

    asyncio.run_coroutine_threadsafe(_send(), _response_loop)

def broadcast_audio(data: bytes):
    if not _clients or _response_loop is None:
        return
    async def _send():
        to_remove = []
        for ws in list(_clients):
            try:
                await ws.send(data)
            except Exception:
                to_remove.append(ws)
        for ws in to_remove:
            _clients.discard(ws)
    asyncio.run_coroutine_threadsafe(_send(), _response_loop)

async def main():
    print("Starting voice processing...")

    # launch response websocket server in separate daemon thread
    threading.Thread(target=_start_response_ws_server, daemon=True).start()

    agent = AIAgent()
    process = None
    try:
        process = speech_to_text.start_speech_recognition()
        
        for speech_text in speech_to_text.get_speech_text_stream(process):
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