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
    - chat_service.py: Orchestrates chat sessions including audio buffering, transcription, agent response, and TTS.
  - exceptions/: custom exceptions for chat feature.
- speech/
  - repositories/
    - speech_repository.py: Handles text-to-speech synthesis using edge-tts (pinned to v6.1.12).
  - services/
    - speech_service.py: Business logic for TTS, uses SpeechRepository.
- agent/
  - repositories/
    - agent_repository.py: Handles LLM interactions for agent responses.
  - services/
    - agent_service.py: Business logic for agent response generation.
- common/
  - types/
    - exceptions.py: base exception classes for Sawt, includes error code and status.

### Error Handling Design Summary

Use **exceptions for exceptional conditions**, not routine control flow.

**Good pattern:** Let low-level libraries raise (e.g. DB timeout, network error), catch them once, wrap in your own exception with added context (query, user id, correlation id), and let a **global exception handler** convert known domain/operational exceptions into structured HTTP responses (status code + JSON).

**Avoid:** Relying on accidental exceptions (`AttributeError`, `TypeError` from `None` dereferences) to represent expected states like “user not found.” For *expected* absences, either:
- Return `None`/`Optional` and check it at the boundary, or
- Raise a deliberate domain exception like `UserNotFound(user_id)`.

**Why:** Intentional exceptions keep the “happy path” clean, preserve clear stack traces, and distinguish *operational errors* (timeouts, not found) from *programmer bugs*.

**Global handler responsibilities:**
- Map known domain/operational exceptions to appropriate HTTP codes.
- Log unexpected exceptions separately (these are bugs) before returning a generic 500.

**Performance note:** Exceptions are fine for rare failures; don’t use them in hot paths for common outcomes (e.g. cache miss).

> **Rule of thumb:** If a situation is part of normal business logic, handle it explicitly. If it violates a contract or an external dependency fails, raise/propagate an exception with context.

## Current Status

- **Backend:**
  - Global exception handling middleware implemented.
  - `BaseSawtException` updated with `code`, `message`, and `status_code`.
  - `TranscriptionRepository` and `TranscriptionService` implemented for Hugging Face ASR.
  - `ChatService` implemented for WebSocket message handling, audio buffering, transcription, agent interaction, and TTS response.
  - `websocket_controller.py` updated to use `ChatService` for 1:1 WebSocket communication.
  - CORS middleware added to `main.py` to allow frontend connections.
  - **Text-to-Speech (TTS):**
    - `SpeechRepository` and `SpeechService` implemented using **Google Cloud Text-to-Speech API**.
    - **Migrated from edge-tts** due to Microsoft blocking automated access with 403 errors (Sec-MS-GEC token requirement).
    - Enhanced logging in `speech_repository.py`:
      - Validates input text (prevents empty/whitespace-only text).
      - Logs text being synthesized (first 200 chars) for debugging.
      - Logs success with audio byte size.
      - Logs detailed error messages with text context on failures.
    - Uses "en-US-Neural2-J" voice (male neural voice, similar quality to previous Brian voice).
    - **Setup Requirements:**
      - Google Cloud credentials file: `gen-lang-client-0769363257-ef37cf535274.json` in backend folder
      - Credentials file mounted in Docker containers with `GOOGLE_APPLICATION_CREDENTIALS` env var
      - Free tier: 1 million characters/month for WaveNet voices
  - `AgentService` and `AgentRepository` implemented for LLM-based agent responses.
- **Frontend:**
  - `useMicrophone` updated to propagate `stop` events from the audio worklet.
  - `useChatMicrophone` updated to send `{"event":"stop"}` to the backend.
  - `useChatWebsocket` updated to use the correct backend WebSocket URL (`/ws/chat`) and parse incoming text messages (`{"type":"text","payload":"..."}`).

All core modules and feature directories are scaffolded and ready for implementation. Services, repositories, and DTOs will be populated as features evolve.
