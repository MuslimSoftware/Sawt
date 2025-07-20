# Backend Implementation Plan

This document outlines the current Sawt backend structure.

## Core Technology Stack

- Framework: FastAPI
- Server: Uvicorn
- Language: Python

## Architecture: Feature-Based N-Layered Design

### infrastructure/
- core/
  - config.py: application configuration using Pydantic BaseSettings.
- middlewares/
  - exception_handler.py: Global exception handler for FastAPI.
  - rate_limiting.py: middleware for client request rate limiting.
- logging/
  - logging.py: sets up Python logging configuration.
- network/
  - connection_manager.py: Manages individual WebSocket connections (low-level).

### features/
- chat/
  - controllers/
    - websocket_controller.py: WebSocket endpoint for chat, delegates to ChatManager and handles exceptions from transcription service.
  - managers/
    - chat_manager.py: Handles chat-specific logic (audio buffering, transcription, messaging), uses ConnectionManager.
  - repositories/
    - transcription_repository.py: Handles API calls to Hugging Face for transcription.
  - services/
    - transcription_service.py: Business logic for transcription, uses TranscriptionRepository and builds WAV.
  - exceptions/: custom exceptions for chat feature.
- common/
  - types/
    - exceptions.py: base exception classes for Sawt, includes error code and status.

## Current Status

- **Backend:**
  - Global exception handling middleware implemented.
  - `BaseSawtException` updated with `code`, `message`, and `status_code`.
  - `TranscriptionRepository` and `TranscriptionService` implemented for Hugging Face ASR.
  - `ChatManager` implemented for WebSocket message handling, audio buffering, and delegation to `TranscriptionService`.
  - `websocket_controller.py` updated to use `ChatManager` for 1:1 WebSocket communication.
  - CORS middleware added to `main.py` to allow frontend connections.
- **Frontend:**
  - `useMicrophone` updated to propagate `stop` events from the audio worklet.
  - `useChatMicrophone` updated to send `{"event":"stop"}` to the backend.
  - `useChatWebsocket` updated to use the correct backend WebSocket URL (`/ws/chat`) and parse incoming text messages (`{"type":"text","payload":"..."}`).

All core modules and feature directories are scaffolded and ready for implementation. Services, repositories, and DTOs will be populated as features evolve.
