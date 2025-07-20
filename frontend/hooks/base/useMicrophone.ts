import { useEffect, useState } from 'react';

const WORKLET_PATH = '/audio-worklet/down-sampler.js';

type Cb = () => void;
interface Props {
  onData?: (buf: ArrayBuffer) => void;
  onStart?: Cb;
  onStop?: Cb;
  voiceThreshold?: number;
}

/**
 * Grants mic access, streams down-sampled PCM to `onData`,
 * and returns both the permission flag and the live MediaStream.
 */
export function useMicrophone({ onData, onStart, onStop, voiceThreshold }: Props) {
  const [{ granted, stream }, set] = useState<{ granted: boolean; stream: MediaStream | null }>({ granted: false, stream: null });

  useEffect(() => {
    let ctx: AudioContext;
    let node: AudioWorkletNode;
    let mic: MediaStream;
    let cancelled = false;

    (async () => {
      try {
        mic = await navigator.mediaDevices.getUserMedia({ audio: true });
        if (cancelled) return mic.getTracks().forEach(t => t.stop());

        ctx = new AudioContext();
        await ctx.audioWorklet.addModule(WORKLET_PATH);
        if (ctx.state !== 'running') await ctx.resume().catch(() => {});

        node = new AudioWorkletNode(ctx, 'down-sampler', { processorOptions: { voiceThreshold } } as any);
        node.port.onmessage = ({ data }) => {
          data.event === 'stop' && onStop?.();
          data.audio && onData?.(data.audio);
          data.event === 'start' && onStart?.();
        };

        ctx.createMediaStreamSource(mic).connect(node);
        node.connect(ctx.destination);
        set({ granted: true, stream: mic });
      } catch (e) {
        console.error('Microphone setup failed:', e);
      }
    })();

    return () => {
      cancelled = true;
      stream?.getTracks().forEach(t => t.stop());
      node?.disconnect();
      ctx?.close().catch(() => {});
      set({ granted: false, stream: null });
    };
  }, [voiceThreshold, onData, onStart, onStop]);

  return { isMicrophoneGranted: granted, micStream: stream } as const;
}
