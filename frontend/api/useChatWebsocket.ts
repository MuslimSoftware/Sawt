import { useCallback, useEffect, useRef, useState } from 'react';
import { useWebSocket } from './useWebsocket';
import { useChat } from '@/contexts/ChatContext';

const DEFAULT_CHAT_URL = 'ws://localhost:8765';

export const useChatWebsocket = () => {
  /* -------------- audio playback -------------- */
  const [playbackStream, setPlaybackStream] = useState<MediaStream | null>(null);
  const audioCtxRef = useRef<AudioContext | null>(null);
  const destRef = useRef<MediaStreamAudioDestinationNode | null>(null);

  /* helper ↴ converts Int16 PCM to a ready-to-play AudioBuffer */
  const pcmToBuffer = (pcm: ArrayBuffer, ctx: AudioContext) => {
    const int16 = new Int16Array(pcm);
    const float32 = new Float32Array(int16.length);
    for (let i = 0; i < int16.length; i++) float32[i] = int16[i] / 0x7fff;
    const buf = ctx.createBuffer(1, float32.length, 16_000);
    buf.copyToChannel(float32, 0);
    return buf;
  };

  /* -------------- websocket handler -------------- */
  const onMessage = useCallback((event: MessageEvent) => {
    console.log("[useChatWebsocket] onMessage", event);
    // 👀 binary = audio
    if (event.data instanceof ArrayBuffer) {
      const ctx  = audioCtxRef.current ?? new AudioContext();
      const dest = destRef.current  ?? ctx.createMediaStreamDestination();

      audioCtxRef.current = ctx;
      destRef.current     = dest;

      const arrBuf = event.data.slice(0);
      ctx.decodeAudioData(arrBuf).then(decoded => {
        const src = ctx.createBufferSource();
        src.buffer = decoded;
        src.connect(dest);
        src.connect(ctx.destination);
        if (ctx.state === 'suspended') ctx.resume?.().catch(() => {});
        src.start();

        if (!playbackStream) setPlaybackStream(dest.stream);
      }).catch(() => {
        // fallback to raw PCM conversion
        const src = ctx.createBufferSource();
        src.buffer = pcmToBuffer(event.data, ctx);
        src.connect(dest);
        src.connect(ctx.destination);
        if (ctx.state === 'suspended') ctx.resume?.().catch(() => {});
        src.start();
        if (!playbackStream) setPlaybackStream(dest.stream);
      });
      return;
    }

    // 📝 string = text chat (JSON or plain text)
    try {
      const msg = JSON.parse(event.data);
      // console.log("🔊 Message", msg);
    //   setMessages((prev: string[]) => [...prev, msg]);
    } catch {
    //   setMessages((prev: string[]) => [...prev, { role: 'server', content: event.data }]);
    }
  }, [playbackStream]);

  /* -------------- connect WebSocket -------------- */
  const { isConnected, isConnecting, error, sendData } = useWebSocket({
    url: DEFAULT_CHAT_URL,
    onMessage,
  });

  /* -------------- cleanup -------------- */
  useEffect(() => {
    return () => {
      audioCtxRef.current?.close().catch(() => {});
    };
  }, []);

  return { isConnected, isConnecting, error, playbackStream, sendData };
};
