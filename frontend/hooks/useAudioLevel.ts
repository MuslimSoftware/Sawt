import { useEffect, useState } from 'react';

interface Options {
  /** Decoded audio coming back from the server (optional). */
  playbackStream?: MediaStream | null;
}

/**
 * Returns a single RMS-style level (0-1) that reflects both the microphone
 * and an optional playback stream.
 */
export const useAudioLevel = (
  micStream: MediaStream | null,
  { playbackStream }: Options = {}
) => {
  const [level, setLevel] = useState(0);

  useEffect(() => {
    if (!micStream) return;

    const ctx = new AudioContext();
    let cancelled = false; // ← guard against Strict-Mode unmount

    (async () => {
      try {
        await ctx.audioWorklet.addModule('/audio-worklet/level-meter.js');
        if (cancelled) return;                     // context is dead

        const meter = new AudioWorkletNode(ctx, 'level-meter', {
          numberOfInputs : 2,
          numberOfOutputs: 0,
        });

        // mic → input 0
        ctx.createMediaStreamSource(micStream).connect(meter, 0, 0);

        // server playback → input 1
        if (playbackStream)
          ctx.createMediaStreamSource(playbackStream).connect(meter, 0, 1);

        meter.port.onmessage = (e) => {
          if (!cancelled) setLevel(e.data as number);
        };
      } catch (err) {
        console.error(err);
      }
    })();

    return () => {
      cancelled = true;
      ctx.close().catch(() => {});
      // We *didn’t* create the streams, so we don’t stop their tracks here.
    };
  }, [micStream, playbackStream]);

  return {level};
};
