import { useMicrophone } from "@/permissions/useMicrophone";
import { useCallback, useEffect } from "react";

export const useChatMicrophone = (sendData: (data: string | ArrayBuffer) => void) => {
    const onData = useCallback((buf: ArrayBuffer) => {
        // console.log("[useChatMicrophone] Audio bytes received", buf.byteLength);
        sendData(buf);
      }, [sendData]);

    const onStart = useCallback(() => {
      console.log("[useChatMicrophone] Start speaking");
    }, []);

    const onStop = useCallback(() => {
      console.log("[useChatMicrophone] Stop speaking");
    }, []);
    
    const { isMicrophoneGranted, micStream } = useMicrophone({ onData, onStart, onStop, voiceThreshold: 0.05, silenceDelayMs: 1000 });

    return { isMicrophoneGranted, micStream };
}   
