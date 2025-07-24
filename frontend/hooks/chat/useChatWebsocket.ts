"use client";

import { useEffect, useCallback, useState } from "react";
import { useAudioPlayback } from "@/hooks/base/useAudioPlayback";
import { useWebsocket } from "@/hooks/base/useWebsocket";
import { Message } from "@/contexts/ChatContext";

const WS_URL = process.env.NEXT_PUBLIC_BACKEND_WS || "wss://sawt-api.younesbenketira.com/ws/chat";

export const useChatWebsocket = ({setMessages}: {setMessages: React.Dispatch<React.SetStateAction<Message[]>>}) => {
  const { play, stopAll, playbackStream } = useAudioPlayback();
  const [isLoading, setIsLoading] = useState(false);
  const [isReceiving, setIsReceiving] = useState(false);

  const handleMessage = useCallback(
    (event: MessageEvent) => {
      // console.log("Received message:", event.data);
      // Play incoming audio stream
      if (event.data instanceof ArrayBuffer) {
        setIsLoading(false);
        setIsReceiving(true);
        play(event.data);
        return;
      }

      // Handle other message types
      const message = JSON.parse(event.data as string);
      
      switch (message.type) {
        case "control":
          if (message.event === "stop_audio") {
            stopAll();
            setIsReceiving(false);
          }
          break;
        case "text":
          setIsLoading(false);
          setMessages((prev) => [...prev, { role: message.role, content: message.text }]);
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
    if (!isReceiving) {
      setIsLoading(true);
    }
    sendData(data);
  }, [sendData, isReceiving]);

  return { sendData: send, playbackStream, isConnected, isConnecting, error, isLoading } as const;
};
