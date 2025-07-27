# Sawt (صوت)
“Sawt” means “voice” in Arabic.

A DIY voice agent:
- streams voice to server
- Transcribes speech ([whisper](https://huggingface.co/openai/whisper-large-v3))
- Prompts LLM ([DSPy](https://dspy.ai/))
- TTS ([edge-tts](https://github.com/rany2/edge-tts))

Try it out: https://sawt.younesbenketira.com

<video src="https://github.com/user-attachments/assets/7237e5c2-5333-467c-b669-e9b4280a5193" controls="controls" style="max-width: 100%;"></video>

## Features

- 🎤 Real-time microphone input with mobile support
- 🗣️ Speech-to-text using Whisper
- 🔊 Edge TTS speech synthesis
- 🤖 AI-powered voice responses
- 🔄 WebSocket-based streaming
- 🐳 Docker containerization for local and production environments

## Quick Start

### Prerequisites
- Docker and Docker Compose
- A `.env.dev` and `.env.prod` file (based on `env.example`)

### Local Development
```bash
# Build the services using the dev-specific compose file and .env.dev
docker compose -f docker-compose.dev.yml --env-file .env.dev build

# Start the services
docker compose -f docker-compose.dev.yml --env-file .env.dev up

# Access the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

### Production Deployment
```bash
# Build the services using the .env.prod file
docker compose --env-file .env.prod build

# Start the services in detached mode
docker compose --env-file .env.prod up -d

# Access via your server's IP or domain
# Frontend: http://YOUR_SERVER_IP:3000
# Backend: http://YOUR_SERVER_IP:8000
```

## Architecture

- **Frontend**: Next.js with TypeScript, real-time audio processing
- **Backend**: Python FastAPI with WebSocket support
- **Speech Recognition**: Whisper
- **AI Integration**: Your chosen AI model

## License

This project is licensed under a **Non-Commercial License**. See [LICENSE](LICENSE) for details.

**Key Terms:**
- ✅ Personal and educational use allowed
- ✅ Open source contributions welcome
- ❌ Commercial use prohibited
- ❌ Monetization not allowed

## Contributing

Contributions are welcome! Please ensure any contributions maintain the non-commercial nature of this project.

## Agent Metadata

This repository's `AGENTS.md` is intended for opencode to know about the overall repository. Additional `AGENTS.md` files reside in the `backend/` and `frontend/` directories to describe their respective logic contexts.

## Support

For questions or support, please open an issue on GitHub.

---

**Note**: This project is designed for personal and educational use only. Commercial use is not permitted under the license terms.
