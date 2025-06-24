#!/usr/bin/env python3

import subprocess
import os
import threading
import asyncio
import websockets
from typing import Generator
import time

WORKSPACE_ROOT = "/Users/younesbenketira/Code/personal/Sawt"
WEBSOCKET_PORT = 8765  # Front-end will connect here
PCM_SAMPLE_RATE = 16000  # Must match --sample-rate passed to Rust

# Exposed globals for other modules (e.g., voice_bridge) to broadcast
CLIENTS = set()
WS_LOOP = None

def _start_ws_server(proc_stdin):
    """Run a WebSocket server that forwards binary messages to the Rust stdin."""

    async def handler(websocket, *_):
        CLIENTS.add(websocket)
        peer = websocket.remote_address
        print(f"🔌 WebSocket client connected: {peer}")
        try:
            async for msg in websocket:
                if isinstance(msg, bytes):
                    try:
                        proc_stdin.write(msg)
                        proc_stdin.flush()
                    except Exception as e:
                        print(f"❌ Failed to write to Rust stdin: {e}")
                        break
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"❌ WebSocket error with {peer}: {e}")
        finally:
            CLIENTS.discard(websocket)
            print(f"🔌 WebSocket client disconnected: {peer}")

    async def run():
        async with websockets.serve(handler, "0.0.0.0", WEBSOCKET_PORT, max_size=None):
            await asyncio.Future()  # run forever

    global WS_LOOP
    WS_LOOP = asyncio.new_event_loop()
    asyncio.set_event_loop(WS_LOOP)
    WS_LOOP.run_until_complete(run())

    # wait until WS_LOOP is initialized by the server thread
    for _ in range(50):  # up to ~5 seconds
        if WS_LOOP is not None:
            break
        time.sleep(0.1)

def start_speech_recognition():
    """Start the Rust speech recognition subprocess (stdin mode) and WS gateway."""
    # Build command to run Rust binary via cargo
    cmd = [
        "cargo",
        "run",
        "--manifest-path",
        "Core/input/app/Cargo.toml",
        "--",
        "--source",
        "stdin",
        "--sample-rate",
        str(PCM_SAMPLE_RATE),
    ]

    try:
        process = subprocess.Popen(
            cmd,
            cwd=WORKSPACE_ROOT,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=False,
            bufsize=0,
        )

        # Start websocket server on separate daemon thread
        server_thread = threading.Thread(
            target=_start_ws_server, args=(process.stdin,), daemon=True
        )
        server_thread.start()

        # wait until WS_LOOP set by server thread
        for _ in range(50):
            if WS_LOOP is not None:
                break
            time.sleep(0.1)

        print(
            f"🛰️  WebSocket audio server running on ws://localhost:{WEBSOCKET_PORT} (16 kHz LE16 mono)"
        )
        return process
    except Exception as e:
        print(f"❌ Failed to start speech recognition: {e}")
        raise


def get_speech_text_stream(process) -> Generator[str, None, None]:
    """Yield transcribed lines from Rust process stdout."""
    try:
        if process.stdout is None:
            return
        for raw in iter(process.stdout.readline, b""):
            if not raw:
                break
            line = raw.decode("utf-8", errors="ignore").strip()
            if line:
                yield line
    except Exception as e:
        print(f"❌ Speech recognition stream error: {e}")
    finally:
        if process:
            process.terminate() 