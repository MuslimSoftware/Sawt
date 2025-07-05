import { useMicrophone } from "@/hooks/core/useMicrophone";
import { useCallback, useEffect, useState, useRef } from "react";

// Toggle this to test different muting strategies
const USE_AUDIO_CONTEXT_SUSPEND = false; // Set to true to use suspend/resume, false for audio-only filtering

export const useChatMicrophone = (sendData: (data: string | ArrayBuffer) => void) => {
    const [muted, setMuted] = useState(false);
    const mutedRef = useRef(muted);

    // Keep ref in sync with state
    useEffect(() => {
        mutedRef.current = muted;
    }, [muted]);

    const onData = useCallback((buf: ArrayBuffer) => {
        if (!mutedRef.current) {
          sendData(buf);
        }
      }, [sendData]);

    const onStart = useCallback(() => {
      // Voice started
    }, []);
    
    const { isMicrophoneGranted, micStream, ctx } = useMicrophone({ onData, onStart, voiceThreshold: 0.05 });

    useEffect(() => {
        if (!ctx) return;
        
        if (USE_AUDIO_CONTEXT_SUSPEND) {
            if (muted) {
                ctx.suspend().catch(() => {});
            } else {
                if (ctx.state !== 'running') {
                    ctx.resume().catch(() => {});
                }
            }
        } else {
            // Keep AudioContext running, just filter audio data in onData callback
            if (ctx.state !== 'running') {
                ctx.resume().catch(() => {});
            }
        }
    }, [muted, ctx]);

    const toggleMute = useCallback(() => {
        setMuted(m => !m);
    }, [muted]);

    return { isMicrophoneGranted, micStream, muted, toggleMute };
}   
