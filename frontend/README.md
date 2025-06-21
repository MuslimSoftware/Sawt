# Sawt Front-End

This is a minimal Next.js app that captures microphone audio, down-samples to 16 kHz, encodes as 16-bit little-endian PCM and streams it over WebSocket to the local Sawt backend running at `ws://localhost:8765`.

## Quick start

```bash
cd frontend
npm install          # or: pnpm install / yarn
npm run dev          # open http://localhost:3000
```

Make sure you have the Sawt Python backend running:

```bash
python Core/execution/voice_bridge.py
```

You should see transcriptions in the terminal and hear synthesized replies. 