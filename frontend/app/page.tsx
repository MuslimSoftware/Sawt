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
  const [userSpeaking, setUserSpeaking] = useState(false);
  const [aiSpeaking, setAISpeaking] = useState(false);
  const lastVoiceRef = useRef<number>(0);

  const mediaStreamRef = useRef<MediaStream | null>(null);
  const processorRef = useRef<ScriptProcessorNode | null>(null);
  const audioCtxRef = useRef<AudioContext | null>(null);

  const audioRef = useRef<HTMLAudioElement | null>(null);

  // Dark mode colors
  const bgColor = "#1a1a1d";
  const textColor = "#f5f5f5";

  const fadeLevels = [1, 0.75, 0.55, 0.35, 0.15];

  type ChatMsg = { role: 'user' | 'ai'; text: string };
  const [chatMessages, setChatMessages] = useState<ChatMsg[]>([]);

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
          if (obj.control === "stop_audio") {
            if (audioRef.current) {
              audioRef.current.pause();
              audioRef.current = null;
            }
            return;
          }
          if (obj.role === "user" || obj.role === "ai") {
            const newMsg: ChatMsg = { role: obj.role as 'user' | 'ai', text: obj.text } as ChatMsg;
            setChatMessages(prev => [newMsg, ...prev].slice(0, 10));
          }
        } catch {
          // plain string fallback
          const newMsg2: ChatMsg = { role: 'ai', text: e.data as string } as ChatMsg;
          setChatMessages(prev => [newMsg2, ...prev].slice(0, 10));
        }
      } else {
        // Could be audio bytes or JSON in ArrayBuffer (if backend sent text as binary)
        const buf = e.data as ArrayBuffer;
        try {
          const txt = new TextDecoder().decode(buf);
          const obj = JSON.parse(txt);
          if (obj.role === "user" || obj.role === "ai") {
            const newMsg: ChatMsg = { role: obj.role as 'user' | 'ai', text: obj.text } as ChatMsg;
            setChatMessages(prev => [newMsg, ...prev].slice(0, 10));
            return;
          }
        } catch {
          // not JSON, treat as audio
        }
        console.log("🔊 Audio bytes received", buf.byteLength);
        const blob = new Blob([buf], { type: "audio/mpeg" });
        const url = URL.createObjectURL(blob);
        const audio = new Audio(url);
        audioRef.current = audio;
        audio.onplay = () => {
          setUserSpeaking(false);
        };
        audio.onended = () => setUserSpeaking(false);
        audio.onerror = () => setUserSpeaking(false);
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
          if (userSpeaking) return;

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
      ? baseSize + 40
      : baseSize;

  const circleStyle: React.CSSProperties = {
    width: size,
    height: size,
    borderRadius: "50%",
    background: userSpeaking
      ? "#28a745" /* green */
      : "#ffffff",
    border: "none",
    transition:
      "width 0.05s linear, height 0.05s linear, box-shadow 0.05s linear, background 0.3s ease",
    boxShadow: userSpeaking
      ? `0 0 ${20 + volume * 120}px rgba(40,167,69,0.9)`
      : "none",
    backdropFilter: userSpeaking ? "blur(2px)" : "none",
    margin: "0 auto",
  };

  const columnStyle: React.CSSProperties = {
    paddingTop: 50,
    color: textColor,
    display: "flex",
    flexDirection: "column",
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
        <div style={{ flex: 1, display: "flex", justifyContent: "center", flexDirection: "column", alignItems: "center" }}>
          {/* circle */}
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: '70%' }}>
            <div style={{position: "relative", width: '100%', height: 180}}>
              <div style={circleStyle} />
            </div>
            <div className="chatWrap" style={{ position:'relative' }}>
              <div style={{ ...columnStyle, position: 'absolute', width:'100%', textAlign:'left', overflowY:'hidden' }}>
                {chatMessages.map((msg, idx) => {
                  const opacity = fadeLevels[idx] ?? 0.1;
                  const isUser = msg.role === 'user';
                  return (
                    <div key={idx} style={{ display: 'flex', justifyContent: isUser ? 'flex-end' : 'flex-start', opacity, transition: 'opacity 0.3s' }}>
                      <div style={{
                        maxWidth: '70%',
                        padding: '8px 12px',
                        borderRadius: 12,
                        background: isUser ? 'transparent' : 'rgba(255,255,255,0.12)',
                        color: '#f5f5f5',
                        margin: '4px 0'
                      }}>{msg.text}</div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
          {/* chat messages */}
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
      <style jsx>{`
        .chatWrap{width:90vw;max-width:90vw;}
        @media(min-width:768px){.chatWrap{width:30vw;max-width:30vw;}}
        @media(min-width:1280px){.chatWrap{width:25vw;max-width:25vw;}}
      `}</style>
    </>
  );
} 