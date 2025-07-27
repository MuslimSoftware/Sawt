"use client";

import { useEffect, useCallback, useState } from "react";
import { useAudioPlayback } from "@/hooks/base/useAudioPlayback";
import { useWebsocket } from "@/hooks/base/useWebsocket";
import { Message } from "@/contexts/ChatContext";

const WS_URL = process.env.NEXT_PUBLIC_BACKEND_WS || "wss://sawt-api.younesbenketira.com/ws/chat";

export const useChatWebsocket = ({setMessages, setSystemState}: {setMessages: React.Dispatch<React.SetStateAction<Message[]>>, setSystemState: React.Dispatch<React.SetStateAction<string>>}) => {
  const { play, stopAll, playbackStream } = useAudioPlayback();
  const [isLoading, setIsLoading] = useState(false);

  const handleMessage = useCallback(
    (event: MessageEvent) => {
      if (event.data instanceof ArrayBuffer) {
        setIsLoading(false);
        play(event.data);
        return;
      }

      // Handle other message types
      const message = JSON.parse(event.data as string);
      
      switch (message.type) {
        case "control":
          if (message.event === "stop_audio") {
            stopAll();
          }
          break;
        case "text":
          setMessages((prev) => [...prev, { role: message.role, content: message.text }]);
          setSystemState(undefined);
          break;
        case "event":
          setSystemState(message.event);
          break;
      }
    },
    [play, stopAll, setMessages]
  );

  const { sendData, isConnected, isConnecting, error } = useWebsocket(
    WS_URL!,
    handleMessage
  );

  const send = useCallback((data: string | ArrayBuffer) => {
    if (!(typeof data === "string" && data.includes(`{"event":"stop"}`))) {
      setIsLoading(true);
    }
    
    sendData(data);
  }, [sendData]);

  return { sendData: send, playbackStream, isConnected, isConnecting, error, isLoading } as const;
};
