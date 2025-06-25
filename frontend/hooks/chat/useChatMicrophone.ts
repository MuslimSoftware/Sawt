import { useMicrophone } from "@/hooks/core/useMicrophone";
import { useCallback, useEffect, useState } from "react";

export const useChatMicrophone = (sendData: (data: string | ArrayBuffer) => void) => {
    const [muted, setMuted] = useState(false);

    const onData = useCallback((buf: ArrayBuffer) => {
        if (!muted) {
          sendData(buf);
        }
      }, [sendData, muted]);

    const onStart = useCallback(() => {
      console.log("[useChatMicrophone] Start speaking");
    }, []);

    const onStop = useCallback(() => {
      console.log("[useChatMicrophone] Stop speaking");
    }, []);
    
    const { isMicrophoneGranted, micStream, ctx } = useMicrophone({ onData, onStart, onStop, voiceThreshold: 0.05, silenceDelayMs: 1000 });

    useEffect(() => {
        if (!ctx) return;
        if (muted) ctx.suspend().catch(() => {});
        else ctx.state !== 'running' && ctx.resume().catch(() => {});
    }, [muted, ctx]);

    return { isMicrophoneGranted, micStream, muted, toggleMute: () => setMuted(m => !m) };
}   
