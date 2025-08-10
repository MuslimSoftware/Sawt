# Sawt Front-End

This is a minimal Next.js app that captures microphone audio, down-samples to 16 kHz, encodes as 16-bit little-endian PCM and streams it over WebSocket to the local Sawt backend running at `ws://localhost:8000/ws`.

## Quick start

```bash
cd frontend
npm install          # or: pnpm install / yarn
npm run dev          # open http://localhost:3000
```

Make sure you have the Sawt Python backend running:

```bash
cd backend
uvicorn server:app --host 0.0.0.0 --port 8000 --reload --reload-dir app
```

You should see transcriptions in the terminal and hear synthesized replies. 