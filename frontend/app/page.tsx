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
  const wsRespRef = useRef<WebSocket | null>(null);
  const [connected, setConnected] = useState(false);
  const [permissionGranted, setPermissionGranted] = useState<boolean | null>(null);
  const [volume, setVolume] = useState(0);
  const [responseText, setResponseText] = useState<string | null>(null);
  const [userMessages, setUserMessages] = useState<string[]>([]);
  const [aiMessages, setAIMessages] = useState<string[]>([]);
  const [aiSpeaking, setAISpeaking] = useState(false);
  const [userSpeaking, setUserSpeaking] = useState(false);
  const lastVoiceRef = useRef<number>(0);

  const mediaStreamRef = useRef<MediaStream | null>(null);
  const processorRef = useRef<ScriptProcessorNode | null>(null);
  const audioCtxRef = useRef<AudioContext | null>(null);

  // Dark mode colors
  const bgColor = "#1a1a1d";
  const textColor = "#f5f5f5";

  const fadeLevels = [1, 0.75, 0.55, 0.35, 0.15];

  // Connect audio streaming websocket immediately
  useEffect(() => {
    console.log("Connecting to audio WebSocket backend...");
    const ws = new WebSocket("ws://localhost:8765");
    ws.binaryType = "arraybuffer";
    ws.onopen = () => {
      console.log("Audio WebSocket opened");
      setConnected(true);
    };
    ws.onclose = () => setConnected(false);
    ws.onerror = () => setConnected(false);
    wsRef.current = ws;

    return () => ws.close();
  }, []);

  // Connect response websocket
  useEffect(() => {
    const wsResp = new WebSocket("ws://localhost:8766");
    wsResp.binaryType = "arraybuffer";
    wsResp.onmessage = (e) => {
      console.log("🔊 Response message", e);
      if (typeof e.data === "string") {
        try {
          const obj = JSON.parse(e.data as string);
          if (obj.role === "user") {
            console.log("User message", obj.text);
            setUserMessages((prev) => [...prev, obj.text]);
          } else if (obj.role === "ai") {
            console.log("AI message", obj.text);
            setAIMessages((prev) => [...prev, obj.text]);
          }
        } catch {
          // plain string fallback
          setAIMessages((prev) => [...prev, e.data as string]);
        }
      } else {
        // Could be audio bytes or JSON in ArrayBuffer (if backend sent text as binary)
        const buf = e.data as ArrayBuffer;
        try {
          const txt = new TextDecoder().decode(buf);
          const obj = JSON.parse(txt);
          if (obj.role === "user") {
            console.log("User message (bin)", obj.text);
            setUserMessages((prev) => [...prev, obj.text]);
            return;
          } else if (obj.role === "ai") {
            console.log("AI message (bin)", obj.text);
            setAIMessages((prev) => [...prev, obj.text]);
            return;
          }
        } catch {
          // not JSON, treat as audio
        }
        console.log("🔊 Audio bytes received", buf.byteLength);
        const blob = new Blob([buf], { type: "audio/mpeg" });
        const url = URL.createObjectURL(blob);
        const audio = new Audio(url);
        audio.onplay = () => setAISpeaking(true);
        audio.onended = () => setAISpeaking(false);
        audio.onerror = () => setAISpeaking(false);
        audio.play();
      }
    };
    wsRespRef.current = wsResp;
    return () => wsResp.close();
  }, []);

  // Attempt to get mic permission & start streaming automatically
  useEffect(() => {
    const obtainMic = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        setPermissionGranted(true);
        mediaStreamRef.current = stream;

        const audioCtx = new AudioContext();
        audioCtxRef.current = audioCtx;
        const source = audioCtx.createMediaStreamSource(stream);
        const processor = audioCtx.createScriptProcessor(1024, 1, 1);

        processor.onaudioprocess = (e) => {
          const input = e.inputBuffer.getChannelData(0);
          // Volume (root mean square)
          let sum = 0;
          for (let i = 0; i < input.length; i++) sum += input[i] * input[i];
          const rms = Math.sqrt(sum / input.length);
          setVolume(rms); // 0..1 (~)

          const now = Date.now();
          const voiceThreshold = 0.08;
          const silenceDelayMs = 600;

          if (rms > voiceThreshold) {
            lastVoiceRef.current = now;
            if (!userSpeaking) setUserSpeaking(true);
          } else {
            if (userSpeaking && now - lastVoiceRef.current > silenceDelayMs) {
              setUserSpeaking(false);
            }
          }

          // Downsample + send to backend
          const downsampled = downsampleBuffer(input, audioCtx.sampleRate, 16000);
          const pcm = new Int16Array(downsampled.length);
          for (let i = 0; i < downsampled.length; i++) {
            const s = Math.max(-1, Math.min(1, downsampled[i]));
            pcm[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
          }
          if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.send(pcm.buffer);
          }
        };

        source.connect(processor);
        processor.connect(audioCtx.destination);
        processorRef.current = processor;
      } catch (err) {
        console.error("Mic permission denied", err);
        setPermissionGranted(false);
      }
    };

    obtainMic();

    return () => {
      processorRef.current?.disconnect();
      mediaStreamRef.current?.getTracks().forEach((t) => t.stop());
      audioCtxRef.current?.close();
    };
  }, []);

  // Circle size & style
  const baseSize = 180; // px starting size
  const maxExtra = 140; // px at loud voice
  const size = userSpeaking
    ? baseSize + volume * maxExtra
    : aiSpeaking
    ? baseSize + 40 /* fixed bump while AI talks */
    : baseSize;

  const circleStyle: React.CSSProperties = {
    width: size,
    height: size,
    borderRadius: "50%",
    background: aiSpeaking
      ? "#3fa9ff" /* blue */
      : userSpeaking
      ? "#28a745" /* green */
      : "rgba(255,255,255,0.5)",
    border: permissionGranted ? "2px solid #555" : "2px dashed #555",
    transition:
      "width 0.05s linear, height 0.05s linear, box-shadow 0.05s linear, background 0.3s ease",
    boxShadow: aiSpeaking
      ? `0 0 ${30 + (Math.sin(Date.now()/150)*10+10)}px rgba(63,169,255,0.9)`
      : userSpeaking
      ? `0 0 ${20 + volume * 120}px rgba(40,167,69,0.9)`
      : "none",
    backdropFilter: (userSpeaking || aiSpeaking) ? "blur(2px)" : "none",
    margin: "0 auto",
  };

  const columnStyle: React.CSSProperties = {
    padding: 20,
    overflowY: "auto",
    height: "100%",
    color: textColor,
    display: "flex",
    flexDirection: "column",
    position: "relative",
  };

  const transcriptWrapper: React.CSSProperties = {
    position: "absolute",
    bottom: "50%",
    width: "100%",
  };

  return (
    <>
    <main
      style={{
        height: "100vh",
        display: "flex",
        flexDirection: "column",
        background: bgColor,
        color: textColor,
      }}
    >
      {/* Content grid */}
      <div style={{ flex: 1, display: "grid", gridTemplateColumns: "1fr 280px 1fr", alignItems: "stretch" }}>
        {/* User transcript */}
        <div style={{ ...columnStyle, textAlign: "right", alignItems: "flex-end" }}>
          <div style={transcriptWrapper}>
            {userMessages.slice(-5).map((m, idx, arr) => {
              const pos = arr.length - 1 - idx; // 0 = newest
              const opacity = fadeLevels[pos] ?? 0.1;
              const isLatest = pos === 0;
              return (
                <p
                  key={`${idx}-${m}`}
                  style={{
                    margin: "4px 0",
                    opacity,
                    animation: isLatest ? "fadeInUp 0.4s ease" : undefined,
                  }}
                >
                  {m}
                </p>
              );
            })}
          </div>
          <div style={{ marginTop: "auto", paddingTop: 12, alignSelf: "flex-start", textAlign: "left" }}>
            <span
              style={{
                padding: "6px 18px",
                borderRadius: 9999,
                background: connected ? "rgba(40,167,69,0.15)" : "rgba(220,53,69,0.15)",
                color: connected ? "#28a745" : "#dc3545",
                fontWeight: 600,
                fontSize: 14,
                whiteSpace: "nowrap",
              }}
            >
              Status: {connected ? "Online" : "Offline"}
            </span>
          </div>
        </div>

        {/* center circle */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100%" }}>
          <div style={circleStyle} />
        </div>

        {/* AI transcript */}
        <div style={{ ...columnStyle, textAlign: "left", alignItems: "flex-start" }}>
          <div style={transcriptWrapper}>
            {aiMessages.slice(-5).map((m, idx, arr) => {
              const pos = arr.length - 1 - idx;
              const opacity = fadeLevels[pos] ?? 0.1;
              const isLatest = pos === 0;
              return (
                <p
                  key={`${idx}-${m}`}
                  style={{
                    margin: "4px 0",
                    opacity,
                    animation: isLatest ? "fadeInUp 0.4s ease" : undefined,
                  }}
                >
                  {m}
                </p>
              );
            })}
          </div>
        </div>
      </div>
    </main>
    <style jsx global>{`
      @keyframes fadeInUp {
        from {
          opacity: 0;
          transform: translateY(8px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }
    `}</style>
    </>
  );
} 