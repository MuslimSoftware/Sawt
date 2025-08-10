"use client";

import { useRef, useState } from "react";

export const useAudioPlayback = () => {
  const ctxRef = useRef<AudioContext | null>(null);
  const destRef = useRef<MediaStreamAudioDestinationNode | null>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const sourcesRef = useRef<AudioBufferSourceNode[]>([]);

  const ensureCtx = () => {
    if (!ctxRef.current) {
      ctxRef.current = new AudioContext();
    }
    if (!destRef.current) {
      destRef.current = ctxRef.current.createMediaStreamDestination();
      setStream(destRef.current.stream);
    }
    return ctxRef.current;
  };

  const stopAll = () => {
    sourcesRef.current.forEach((s) => {
      try {
        s.stop();
      } catch {}
    });
    sourcesRef.current = [];
  };

  const play = (data: ArrayBuffer) => {
    const ctx = ensureCtx();
    const handle = (buffer: AudioBuffer) => {
      const src = ctx.createBufferSource();
      src.buffer = buffer;
      src.connect(destRef.current!);
      src.connect(ctx.destination);
      src.onended = () => {
        sourcesRef.current = sourcesRef.current.filter((x) => x !== src);
      };
      sourcesRef.current.push(src);
      if (ctx.state === "suspended") ctx.resume().catch(() => {});
      src.start();
    };

    ctx
      .decodeAudioData(data.slice(0))
      .then(handle)
      .catch(() => {
        // assume 16-kHz mono LE16 PCM fallback
        const int16 = new Int16Array(data);
        const float32 = new Float32Array(int16.length);
        for (let i = 0; i < int16.length; i++) float32[i] = int16[i] / 0x7fff;
        const buf = ctx.createBuffer(1, float32.length, 16_000);
        buf.copyToChannel(float32, 0);
        handle(buf);
      });
  };

  return { play, stopAll, playbackStream: stream } as const;
}; 