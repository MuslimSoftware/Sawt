import { useEffect, useRef, useState } from 'react';

const WORKLET_URL = '/audio-worklet/down-sampler.js';

type Cb = () => void;
interface Props {
  /** Called for every 16 kHz Int16-PCM chunk (ArrayBuffer). */
  onData?: (buf: ArrayBuffer) => void;
  onStart?: Cb;
  voiceThreshold?: number;
}

/**
 * Grants mic access, streams down-sampled PCM to `onData`,
 * and returns both the permission flag and the live MediaStream.
 */
export function useMicrophone({ onData, onStart, voiceThreshold }: Props) {
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [granted, setGranted] = useState(false);
  const ctxRef = useRef<AudioContext | null>(null);
  const nodeRef = useRef<AudioWorkletNode | null>(null);
  const callbackRefs = useRef({ onData, onStart });

  // Track callback changes
  useEffect(() => {
    callbackRefs.current = { onData, onStart };
  });

  useEffect(() => {
    let cancelled = false;
    const ctx = ctxRef.current ?? (ctxRef.current = new AudioContext());

    // Add AudioContext state change listener
    const handleStateChange = () => {
      // State changed
    };
    
    ctx.addEventListener('statechange', handleStateChange);

    (async () => {
      try {
        const mic = await navigator.mediaDevices.getUserMedia({ audio: true });
        if (cancelled) {
          return mic.getTracks().forEach(t => t.stop());
        }

        await ctx.audioWorklet.addModule(WORKLET_URL);

        if (ctx.state !== 'running') {
          try { 
            await ctx.resume(); 
          } catch (err) {
            // Failed to resume
          }
        }

        if (cancelled) {
          return mic.getTracks().forEach(t => t.stop());
        }

        const node = new AudioWorkletNode(ctx, 'down-sampler', {
          processorOptions: { voiceThreshold },
        } as any);
        
        nodeRef.current = node;
        
        node.port.onmessage = ({ data }) => {
          if (data.audio) {
            callbackRefs.current.onData?.(data.audio);
          }
          if (data.event === 'start') {
            callbackRefs.current.onStart?.();
          }
        };

        const sourceNode = ctx.createMediaStreamSource(mic);
        sourceNode.connect(node);
        node.connect(ctx.destination);

        setStream(mic);
        setGranted(true);
      } catch (e) {
        if (!cancelled) {
          console.error('Microphone setup failed:', e);
        }
      }
    })();

    return () => {
      cancelled = true;
      
      // Remove event listener
      ctx.removeEventListener('statechange', handleStateChange);
      
      if (stream) {
        stream.getTracks().forEach(t => t.stop());
        setStream(null);
      }
      
      if (nodeRef.current) {
        try {
          nodeRef.current.disconnect();
          nodeRef.current = null;
        } catch (err) {
          // Error disconnecting
        }
      }
      
      if (ctxRef.current && ctxRef.current.state !== 'closed') {
        ctxRef.current.close().catch(() => {});
        ctxRef.current = null;
      }
    };
  }, [voiceThreshold]);

  return { isMicrophoneGranted: granted, micStream: stream, ctx: ctxRef.current } as const;
}
