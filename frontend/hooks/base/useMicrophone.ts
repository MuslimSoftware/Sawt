import { useEffect, useState } from 'react';
import { useLatest } from '../common/useLatest';

const WORKLET_PATH = '/audio-worklet/down-sampler.js';

const AUDIO_CONFIGS = {
  voiceThreshold : 0.06,
  silenceTimeoutMs : 1000,
  preBufferMs    : 500,
  speakingGraceMs: 250,
}

export interface WorkletMessage {
  event?: 'start' | 'stop';
  audio?: ArrayBuffer;
}

/**
 * Grants mic access, streams down-sampled PCM, and returns the live MediaStream
 * along with the latest data packet from the audio worklet.
 */
export function useMicrophone({ onMessage }: { onMessage: (msg: WorkletMessage) => void; }) {
  const [{ granted, stream }, setStreamState] = useState<{ granted: boolean; stream: MediaStream | null }>({ granted: false, stream: null });
  const onMessageRef = useLatest(onMessage);

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

        node = new AudioWorkletNode(ctx, 'down-sampler', {
          processorOptions: { ...AUDIO_CONFIGS }
        });
        node.port.onmessage = ({ data }) => onMessageRef.current(data);

        ctx.createMediaStreamSource(mic).connect(node);
        node.connect(ctx.destination);
        setStreamState({ granted: true, stream: mic });
      } catch (e) {
        console.error('Microphone setup failed:', e);
      }
    })();

    return () => {
      cancelled = true;
      stream?.getTracks().forEach(t => t.stop());
      node?.disconnect();
      ctx?.close().catch(() => {});
      setStreamState({ granted: false, stream: null });
    };
  }, []);

  return { isMicrophoneGranted: granted, micStream: stream } as const;
}
