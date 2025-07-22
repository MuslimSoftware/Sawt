"use client";

import { useEffect, useCallback } from "react";
import { useAudioPlayback } from "@/hooks/base/useAudioPlayback";
import { useWebsocket } from "@/hooks/base/useWebsocket";
import { useChat } from "@/contexts/ChatContext";

const WS_URL = process.env.NODE_ENV === "development" 
  ? "ws://localhost:8000/ws/chat" 
  : process.env.NEXT_PUBLIC_BACKEND_WS;

export const useChatWebsocket = () => {
  const { play, stopAll, playbackStream } = useAudioPlayback();
  const { setMessages } = useChat();

  const handleMessage = useCallback(
    (event: MessageEvent) => {
      // console.log("Received message:", event.data);
      // Play incoming audio stream
      if (event.data instanceof ArrayBuffer) {
        play(event.data);
        return;
      }

      // Handle other message types
      const message = JSON.parse(event.data as string);
      
      switch (message.type) {
        case "control":
          if (message.event === "stop_audio") stopAll();
          break;
        case "text":
          setMessages((prev) => [...prev, { role: message.role, content: message.text }]);
          break;
      }
    },
    [play, stopAll, setMessages]
  );

  const { sendData, isConnected, isConnecting, error } = useWebsocket(
    WS_URL,
    handleMessage
  );

  return { sendData, playbackStream, isConnected, isConnecting, error } as const;
};
