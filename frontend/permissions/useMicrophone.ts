import { useEffect, useRef, useState } from 'react';

const WORKLET_URL = '/audio-worklet/down-sampler.js';

type Cb = () => void;
interface Props {
  /** Called for every 16 kHz Int16-PCM chunk (ArrayBuffer). */
  onData?: (buf: ArrayBuffer) => void;
  onStart?: Cb;
  onStop?: Cb;
  voiceThreshold?: number;
  silenceDelayMs?: number;
}

/**
 * Grants mic access, streams down-sampled PCM to `onData`,
 * and returns both the permission flag and the live MediaStream.
 */
export function useMicrophone({ onData, onStart, onStop, voiceThreshold, silenceDelayMs }: Props) {
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [granted, setGranted] = useState(false);
  const ctxRef = useRef<AudioContext | null>(null);

  useEffect(() => {
    let cancelled = false;
    const ctx = ctxRef.current ?? (ctxRef.current = new AudioContext());

    (async () => {
      try {
        const mic = await navigator.mediaDevices.getUserMedia({ audio: true });
        if (cancelled) 
          return mic.getTracks().forEach(t => t.stop());

        await ctx.audioWorklet.addModule(WORKLET_URL);
        if (ctx.state !== 'running') {
          try { await ctx.resume(); } catch {}
        }
        if (cancelled) 
          return mic.getTracks().forEach(t => t.stop());

        const node = new AudioWorkletNode(ctx, 'down-sampler', {
          processorOptions: { voiceThreshold, silenceDelayMs },
        } as any);
        node.port.onmessage = ({ data }) => {
          if (data.audio) onData?.(data.audio);
          if (data.event === 'start') onStart?.();
          if (data.event === 'stop')  onStop?.();
        };
        ctx.createMediaStreamSource(mic).connect(node);
        node.connect(ctx.destination);

        setStream(mic);
        setGranted(true);
      } catch (e) {
        if (!cancelled) console.error(e);
      }
    })();

    return () => {
      cancelled = true;
      stream?.getTracks().forEach(t => t.stop());
      setStream(null);
      if (ctxRef.current && ctxRef.current.state !== 'closed') {
        ctxRef.current.close().catch(() => {});
        ctxRef.current = null;
      }
    };
  }, []);

  return { isMicrophoneGranted: granted, micStream: stream };
}
