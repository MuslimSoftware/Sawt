"use client";

import React, { useEffect, useRef, useState } from "react";

// @ts-nocheck
// This file is generated for Next.js demo purposes.

function downsampleBuffer(buffer: Float32Array, inSampleRate: number, outSampleRate = 16000) {
  if (inSampleRate === outSampleRate) return buffer;
  const ratio = inSampleRate / outSampleRate;
  const newLen = Math.round(buffer.length / ratio);
  const result = new Float32Array(newLen);
  for (let i = 0; i < newLen; i++) {
    const idx = Math.round(i * ratio);
    result[i] = buffer[idx] || 0;
  }
  return result;
}

export default function Page() {
  const wsRef = useRef<WebSocket | null>(null);
  const [connected, setConnected] = useState(false);
  const [recording, setRecording] = useState(false);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const processorRef = useRef<ScriptProcessorNode | null>(null);
  const audioCtxRef = useRef<AudioContext | null>(null);
  const [responseText, setResponseText] = useState<string | null>(null);

  // Establish websocket on mount
  useEffect(() => {
    console.log("Connecting to WebSocket backend...");
    const ws = new WebSocket("ws://localhost:8765");
    ws.binaryType = "arraybuffer";
    ws.onopen = () => {
      console.log("WebSocket opened");
      setConnected(true);
    };
    ws.onclose = (e) => {
      console.log("WebSocket closed", e);
      setConnected(false);
    };
    ws.onerror = (e) => {
      console.error("WebSocket error", e);
      setConnected(false);
    };
    wsRef.current = ws;

    return () => ws.close();
  }, []);

  // establish response websocket
  useEffect(() => {
    const wsResp = new WebSocket("ws://localhost:8766");
    wsResp.binaryType = "arraybuffer";
    wsResp.onmessage = (e) => {
      if (typeof e.data === "string") {
        const text = e.data as string;
        console.log("💬 AI response received", text);
        setResponseText(text);
      } else {
        // binary audio
        const arrayBuf = e.data as ArrayBuffer;
        console.log("🔊 Audio bytes received", arrayBuf.byteLength);
        const blob = new Blob([arrayBuf], { type: "audio/mpeg" });
        const url = URL.createObjectURL(blob);
        const audio = new Audio(url);
        audio.play();
      }
    };
    return () => wsResp.close();
  }, []);

  const startRecording = async () => {
    if (recording) return;
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaStreamRef.current = stream;

    const audioCtx = new AudioContext(); // browser default sample rate (44.1k or 48k)
    audioCtxRef.current = audioCtx;

    const source = audioCtx.createMediaStreamSource(stream);
    const processor = audioCtx.createScriptProcessor(1024, 1, 1);

    processor.onaudioprocess = (e) => {
      const input = e.inputBuffer.getChannelData(0);
      const downsampled = downsampleBuffer(input, audioCtx.sampleRate, 16000);
      const pcm = new Int16Array(downsampled.length);
      for (let i = 0; i < downsampled.length; i++) {
        let s = Math.max(-1, Math.min(1, downsampled[i]));
        pcm[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
      }
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(pcm.buffer);
        // console.log("▶️  Sent audio chunk", pcm.byteLength);
      } else {
        console.warn("WebSocket not open, dropping audio");
      }
    };

    source.connect(processor);
    processor.connect(audioCtx.destination);

    processorRef.current = processor;
    setRecording(true);
  };

  const stopRecording = () => {
    if (!recording) return;
    processorRef.current?.disconnect();
    mediaStreamRef.current?.getTracks().forEach((t) => t.stop());
    audioCtxRef.current?.close();
    setRecording(false);
  };

  return (
    <main style={{ padding: 40 }}>
      <h1>Sawt Live Transcription</h1>
      <p>
        WebSocket status: {connected ? "🟢 connected" : "🔴 disconnected"}
      </p>
      <button onClick={recording ? stopRecording : startRecording} disabled={!connected}>
        {recording ? "Stop" : "Start"} recording
      </button>
      {responseText && (
        <p style={{ marginTop: 20 }}>Last AI response: {responseText}</p>
      )}
    </main>
  );
} 