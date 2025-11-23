import { useEffect, useState } from 'react';

interface Options {
  /** Decoded audio coming back from the server (optional). */
  playbackStream?: MediaStream | null;
  muted?: boolean;
}

/**
 * Returns separate RMS-style levels (0-1) for microphone and playback streams.
 */
export const useAudioLevel = (
  micStream: MediaStream | null,
  { playbackStream, muted = false }: Options = {}
) => {
  const [micLevel, setMicLevel] = useState(0);
  const [playbackLevel, setPlaybackLevel] = useState(0);

  useEffect(() => {
    if (!micStream) return;

    const ctx = new AudioContext();
    let cancelled = false; // ← guard against Strict-Mode unmount

    (async () => {
      try {
        await ctx.audioWorklet.addModule('/audio-worklet/level-meter.js');
        if (cancelled) return;                     // context is dead

        // Create separate meters for mic and playback
        const micMeter = new AudioWorkletNode(ctx, 'level-meter', {
          numberOfInputs : 1,
          numberOfOutputs: 0,
        });

        const playbackMeter = new AudioWorkletNode(ctx, 'level-meter', {
          numberOfInputs : 1,
          numberOfOutputs: 0,
        });

        // mic → mic meter (via gain for mute control)
        const micSrc = ctx.createMediaStreamSource(micStream);
        const micGain = ctx.createGain();
        micGain.gain.value = muted ? 0 : 1;
        micSrc.connect(micGain).connect(micMeter, 0, 0);

        // server playback → playback meter
        if (playbackStream) {
          ctx.createMediaStreamSource(playbackStream).connect(playbackMeter, 0, 0);
        }

        micMeter.port.onmessage = (e) => {
          if (!cancelled) setMicLevel(e.data as number);
        };

        playbackMeter.port.onmessage = (e) => {
          if (!cancelled) setPlaybackLevel(e.data as number);
        };
      } catch (err) {
        console.error(err);
      }
    })();

    return () => {
      cancelled = true;
      ctx.close().catch(() => {});
      // We *didn't* create the streams, so we don't stop their tracks here.
    };
  }, [micStream, playbackStream, muted]);

  return { micLevel, playbackLevel };
};
