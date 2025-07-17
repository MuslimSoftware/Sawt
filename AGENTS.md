# Sawt Project Description
Sawt is a demo project demonstrating a DIY voice agent. The front end displays a circle that's size matches the current volume level either coming from the user themselves speaking into their mic or the backend streaming the agent's voice (via TTS)

## Frontend
- Components: Contains all components used in the frontend. Pages should only consist of components and no pages should have rogue components defined in them. They should all come from the components folder
- Contexts: Contains all contexts used in the frontend
- hooks: All custom hook definitions used in the frontend organized by semantic usage and layered with abstraction layers
- app: The app itself

## Backend
The backend consists of a clean, layered architecture with two main parts:

### Hardware Layer (`hardware/`)
- **Rust-based speech recognition** using whisper.cpp
- **Voice Activity Detection (VAD)** with energy-based thresholding
- **Real-time audio processing** at 16kHz sample rate
- **Offline speech-to-text** conversion

### Application Layer (`layers/`)
Organized into four distinct layers:

#### 1. Speech Layer (`layers/speech/`)
- **recognition.py**: SpeechRecognitionService - Manages Rust whisper process
- **synthesis.py**: TextToSpeechService - Edge TTS integration
- **pipeline.py**: VoiceProcessingPipeline - Orchestrates speech processing

#### 2. AI Layer (`layers/ai/`)
- **agent.py**: AIAgent - DSPy-based conversation and intent classification

#### 3. Communication Layer (`layers/communication/`)
- **websocket_manager.py**: WebSocketManager - Real-time client communication

#### 4. Configuration Layer (`layers/config/`)
- **settings.py**: Settings - Centralized configuration management

### Main Server (`server.py`)
- **VoiceAssistantServer**: Main orchestrator class
- **FastAPI integration**: HTTP and WebSocket endpoints
- **Graceful shutdown**: Signal handling and resource cleanup

## Architecture Benefits

### Clean Separation of Concerns
- Each layer has a specific responsibility
- Clear interfaces between components
- Easy to test and maintain

### Scalability
- Modular design allows for easy extension
- WebSocket manager supports multiple clients
- Configurable AI parameters

### Reliability
- Comprehensive error handling
- Graceful degradation
- Resource cleanup on shutdown

### Development Experience
- Type hints throughout
- Clear documentation
- Environment-based configuration

