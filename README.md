# Sawt Voice Assistant

A real-time voice assistant built with Next.js, Python FastAPI, and Whisper.cpp for speech-to-text transcription.

## Features

- 🎤 Real-time microphone input
- 🗣️ Speech-to-text using Whisper.cpp
- 🤖 AI-powered voice responses
- 🔄 WebSocket-based streaming
- 🐳 Docker containerization

## Quick Start

### Prerequisites
- Docker and Docker Compose
- VPS or local machine

### Local Development
```bash
# Clone the repository
git clone <your-repo-url>
cd Sawt

# Start the services
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

### Production Deployment
```bash
# Build and start on VPS
docker-compose build
docker-compose up -d

# Access via your VPS IP
# Frontend: http://YOUR_VPS_IP:3000
# Backend: http://YOUR_VPS_IP:8000
```

## Architecture

- **Frontend**: Next.js with TypeScript, real-time audio processing
- **Backend**: Python FastAPI with WebSocket support
- **Speech Recognition**: Whisper.cpp (Rust bindings)
- **AI Integration**: DSPy framework for intelligent responses

## License

This project is licensed under a **Non-Commercial License**. See [LICENSE](LICENSE) for details.

**Key Terms:**
- ✅ Personal and educational use allowed
- ✅ Open source contributions welcome
- ❌ Commercial use prohibited
- ❌ Monetization not allowed

## Contributing

Contributions are welcome! Please ensure any contributions maintain the non-commercial nature of this project.

## Support

For questions or support, please open an issue on GitHub.

---

**Note**: This project is designed for personal and educational use only. Commercial use is not permitted under the license terms. 