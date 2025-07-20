# Sawt Backend

A lightweight FastAPI server for the Sawt Voice Assistant with hot reloading support.

## Quick Start

### Development Mode (with hot reloading)

```bash
# Option 1: Using uvicorn directly
uvicorn server:app --host 0.0.0.0 --port 8000 --reload --reload-dir .

# Option 2: Using the run script
python run.py
```

### Production Mode

```bash
uvicorn server:app --host 0.0.0.0 --port 8000
```

## API Endpoints

- `GET /` - Root endpoint with server info
- `WebSocket /ws` - Real-time communication endpoint

## Features

- ✅ Lightweight FastAPI server
- ✅ Hot reloading for development
- ✅ CORS middleware enabled
- ✅ WebSocket support
- ✅ Environment-based configuration

## Project Structure

```
backend/
├── app/                    # Application modules
│   ├── ai/                # AI agent functionality
│   ├── communication/     # WebSocket and communication
│   ├── config/           # Configuration management
│   └── speech/           # Speech recognition and synthesis
├── server.py             # Main FastAPI application
├── run.py                # Simple uvicorn runner
└── requirements.txt      # Python dependencies
```

## Environment Variables

Create a `.env` file based on `env.example`:

```bash
cp env.example .env
```

Required variables:
- `AI_MODEL` - AI model to use
- `AI_API_KEY` - API key for AI service

## Development

The server uses uvicorn with hot reloading enabled. Any changes to files in the current directory will automatically restart the server. 