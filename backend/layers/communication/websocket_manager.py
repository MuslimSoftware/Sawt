#!/usr/bin/env python3

import asyncio
import json
import threading
from typing import Set, Optional, Callable
import websockets
from dataclasses import dataclass
import logging

# Set up logger
logger = logging.getLogger("WebSocketManager")
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(threadName)s] %(message)s",
)

@dataclass
class WebSocketConfig:
    host: str = "0.0.0.0"
    port: int = 8765
    max_size: Optional[int] = None

class WebSocketManager:
    """Manages WebSocket connections and message broadcasting"""
    
    def __init__(self, config: WebSocketConfig):
        self.config = config
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.ws_loop: Optional[asyncio.AbstractEventLoop] = None
        self.server_thread: Optional[threading.Thread] = None
        self._running = False
        self.audio_processor_stdin = None
        
    def start_server(self, audio_processor_stdin=None) -> None:
        """Start the WebSocket server in a separate thread"""
        if self._running:
            logger.warning("WebSocket server already running")
            return
            
        self.audio_processor_stdin = audio_processor_stdin
        self.server_thread = threading.Thread(
            target=self._run_server, 
            daemon=True
        )
        self.server_thread.start()
        
        # Wait for server to initialize
        for _ in range(50):  # up to ~5 seconds
            if self.ws_loop is not None:
                break
            import time
            time.sleep(0.1)
            
        self._running = True
        logger.info(f"WebSocket server started on ws://{self.config.host}:{self.config.port}")
        
    def _run_server(self):
        """Run the WebSocket server in a separate event loop"""
        
        async def websocket_handler(websocket):
            self.clients.add(websocket)
            peer = websocket.remote_address
            logger.info(f"WebSocket client connected: {peer}")
            
            try:
                async for msg in websocket:
                    if isinstance(msg, bytes) and self.audio_processor_stdin:
                        # Forward binary audio data to Rust process
                        try:
                            self.audio_processor_stdin.write(msg)
                            self.audio_processor_stdin.flush()
                            logger.debug(f"Forwarded {len(msg)} bytes to audio processor from {peer}")
                        except Exception as e:
                            logger.error(f"Failed to write to audio processor: {e}")
                            break
                    elif isinstance(msg, str):
                        # Handle text messages (future use)
                        try:
                            data = json.loads(msg)
                            logger.info(f"Received text message from {peer}: {data}")
                        except json.JSONDecodeError:
                            logger.warning(f"Invalid JSON received from {peer}: {msg}")
                            
            except asyncio.CancelledError:
                logger.info(f"WebSocket handler cancelled for {peer}")
            except Exception as e:
                logger.error(f"WebSocket error with {peer}: {e}")
            finally:
                self.clients.discard(websocket)
                logger.info(f"WebSocket client disconnected: {peer}")

        async def run():
            try:
                async with websockets.serve(
                    websocket_handler, 
                    self.config.host, 
                    self.config.port, 
                    max_size=self.config.max_size
                ):
                    logger.info("WebSocket server event loop running (awaiting connections)")
                    await asyncio.Future()  # run forever
            except Exception as e:
                logger.error(f"WebSocket server failed to start: {e}")

        self.ws_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.ws_loop)
        try:
            self.ws_loop.run_until_complete(run())
        except Exception as e:
            logger.error(f"WebSocket server loop error: {e}")
        
    def broadcast_text(self, role: str, text: str) -> None:
        """Broadcast text message to all connected clients"""
        if not self.clients or self.ws_loop is None:
            logger.debug("No clients to broadcast text to.")
            return

        payload = json.dumps({"type": "text", "role": role, "text": text})

        async def _send():
            disconnected_clients = set()
            for ws in self.clients:
                try:
                    await ws.send(payload)
                    logger.debug(f"Sent text to {ws.remote_address}")
                except Exception:
                    logger.warning(f"Failed to send text to {ws.remote_address}, removing client.")
                    disconnected_clients.add(ws)
            
            # Clean up disconnected clients
            for ws in disconnected_clients:
                self.clients.discard(ws)

        asyncio.run_coroutine_threadsafe(_send(), self.ws_loop)

    def broadcast_audio(self, data: bytes) -> None:
        """Broadcast audio data to all connected clients"""
        if not self.clients or self.ws_loop is None:
            logger.debug("No clients to broadcast audio to.")
            return

        async def _send():
            disconnected_clients = set()
            for ws in self.clients:
                try:
                    await ws.send(data)
                    logger.debug(f"Sent audio to {ws.remote_address}")
                except Exception:
                    logger.warning(f"Failed to send audio to {ws.remote_address}, removing client.")
                    disconnected_clients.add(ws)
            
            # Clean up disconnected clients
            for ws in disconnected_clients:
                self.clients.discard(ws)

        asyncio.run_coroutine_threadsafe(_send(), self.ws_loop)

    def broadcast_control(self, command: str) -> None:
        """Broadcast control command to all connected clients"""
        if not self.clients or self.ws_loop is None:
            logger.debug("No clients to broadcast control to.")
            return

        payload = json.dumps({"type": "control", "command": command})

        async def _send():
            disconnected_clients = set()
            for ws in self.clients:
                try:
                    await ws.send(payload)
                    logger.debug(f"Sent control to {ws.remote_address}")
                except Exception:
                    logger.warning(f"Failed to send control to {ws.remote_address}, removing client.")
                    disconnected_clients.add(ws)
            
            # Clean up disconnected clients
            for ws in disconnected_clients:
                self.clients.discard(ws)

        asyncio.run_coroutine_threadsafe(_send(), self.ws_loop)
        
    def get_clients_count(self) -> int:
        """Get the number of connected clients"""
        count = len(self.clients)
        logger.debug(f"Current client count: {count}")
        return count
        
    def get_clients(self) -> Set[websockets.WebSocketServerProtocol]:
        """Get a copy of the current clients set"""
        logger.debug("Returning copy of clients set.")
        return self.clients.copy()
        
    def get_ws_loop(self) -> Optional[asyncio.AbstractEventLoop]:
        """Get the WebSocket event loop"""
        return self.ws_loop
        
    def is_running(self) -> bool:
        """Check if the WebSocket server is running"""
        logger.debug(f"WebSocket server running: {self._running}")
        return self._running
        
    def stop(self) -> None:
        """Stop the WebSocket server"""
        self._running = False
        if self.ws_loop:
            logger.info("Stopping WebSocket server event loop.")
            self.ws_loop.call_soon_threadsafe(self.ws_loop.stop) 