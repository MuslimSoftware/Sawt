# Sawt Backend - Voice Assistant

A sophisticated voice assistant backend with a clean, layered architecture combining Rust-based speech recognition, Python AI processing, and real-time WebSocket communication.

## Architecture Overview

```
backend/
├── hardware/           # Rust speech recognition (whisper.cpp)
├── layers/            # Python layered architecture
│   ├── speech/        # Speech recognition and TTS
│   ├── ai/           # AI agent and conversation logic
│   ├── communication/ # WebSocket and networking
│   └── config/       # Configuration management
├── server.py          # Main server entry point
└── requirements.txt   # Python dependencies
```

## Quick Start

### Prerequisites

1. **Python 3.8+** with virtual environment
2. **Rust** toolchain for hardware components
3. **Environment variables** for AI model configuration

### Setup

1. **Install Python dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Set environment variables:**
   ```bash
   export AI_MODEL="your-model-identifier"
   export AI_API_KEY="your-api-key"
   export WORKSPACE_ROOT="/path/to/sawt"
   ```

3. **Build Rust components:**
   ```bash
   cd hardware/app
   cargo build --release
   ```

4. **Run the server:**
   ```bash
   python server.py
   ```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AI_MODEL` | AI model identifier | Required |
| `AI_API_KEY` | API key for AI model | Required |
| `WORKSPACE_ROOT` | Project root path | `/Users/younesbenketira/Code/personal/Sawt` |
| `WEBSOCKET_HOST` | WebSocket server host | `0.0.0.0` |
| `WEBSOCKET_PORT` | WebSocket server port | `8765` |
| `PCM_SAMPLE_RATE` | Audio sample rate | `16000` |
| `MAX_CONVERSATION_HISTORY` | AI conversation memory | `20` |
| `AI_TEMPERATURE` | AI response randomness | `0.1` |
| `AI_MAX_TOKENS` | Max AI response length | `4000` |
| `DEFAULT_VOICE` | TTS voice | `en-US-ChristopherNeural` |

### Available TTS Voices

- `en-US-ChristopherNeural`
- `en-US-EricNeural`
- `en-US-GuyNeural`
- `en-US-RogerNeural`
- `en-US-SteffanNeural`

## API Endpoints

### HTTP Endpoints

- `GET /` - Server info and WebSocket URL
- `GET /health` - Health check with status details
- `GET /config` - Current configuration (non-sensitive)

### WebSocket Endpoints

- `WS /ws` - Real-time communication endpoint

## Architecture Layers

### 1. Speech Layer (`layers/speech/`)

**Components:**
- `recognition.py` - Speech-to-text via Rust whisper.cpp
- `synthesis.py` - Text-to-speech via Edge TTS
- `pipeline.py` - Orchestrates speech processing

**Features:**
- Real-time voice activity detection
- Offline speech recognition
- High-quality TTS synthesis
- Audio streaming optimization

### 2. AI Layer (`layers/ai/`)

**Components:**
- `agent.py` - DSPy-based AI agent

**Features:**
- Intent classification
- Conversation memory
- Structured AI interactions
- Error handling and rate limiting

### 3. Communication Layer (`layers/communication/`)

**Components:**
- `websocket_manager.py` - WebSocket server management

**Features:**
- Multi-client support
- Real-time message broadcasting
- Connection management
- Binary audio streaming

### 4. Configuration Layer (`layers/config/`)

**Components:**
- `settings.py` - Centralized configuration management

**Features:**
- Environment variable loading
- Configuration validation
- Type-safe settings
- Default value management

## Development

### Project Structure

```
layers/
├── speech/
│   ├── __init__.py
│   ├── recognition.py      # SpeechRecognitionService
│   ├── synthesis.py        # TextToSpeechService
│   └── pipeline.py         # VoiceProcessingPipeline
├── ai/
│   ├── __init__.py
│   └── agent.py            # AIAgent
├── communication/
│   ├── __init__.py
│   └── websocket_manager.py # WebSocketManager
└── config/
    ├── __init__.py
    └── settings.py         # Settings
```

### Adding New Features

1. **New Layer:** Create directory in `layers/` with `__init__.py`
2. **New Service:** Create class with clear interface
3. **Configuration:** Add to `Settings` class
4. **Integration:** Update `VoiceProcessingPipeline`

### Error Handling

All components include comprehensive error handling:
- Graceful degradation
- Detailed error logging
- Client notification
- Automatic recovery where possible

## Performance

### Optimizations

- **Audio Processing:** 16kHz downsampling, circular buffers
- **Memory Management:** Conversation history limits
- **Network:** Efficient WebSocket binary streaming
- **AI:** Structured prompting for faster responses

### Monitoring

- Health check endpoint (`/health`)
- Real-time status monitoring
- Connection count tracking
- Performance metrics

## Troubleshooting

### Common Issues

1. **Rust build fails:** Ensure Rust toolchain is installed
2. **AI model errors:** Check `AI_MODEL` and `AI_API_KEY` environment variables
3. **WebSocket connection fails:** Verify port 8765 is available
4. **Audio issues:** Check microphone permissions and audio drivers

### Debug Mode

Enable debug logging by setting:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python -u server.py
```

## License

MIT License - see LICENSE file for details. 