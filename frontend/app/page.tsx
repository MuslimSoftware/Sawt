"use client";

import React from "react";
import { useChat } from "@/contexts/ChatContext";
import { useChatWebsocket } from "@/api/useChatWebsocket";
import { useChatMicrophone } from "@/hooks/useChatMicrophone";
import { MicrophoneVisualizer } from "@/components/MicrophoneVisualizer";

export default function Page() {
  const { messages, setMessages } = useChat();
  const { sendData, playbackStream, isConnected, isConnecting, error } =
    useChatWebsocket();
  const { micStream } = useChatMicrophone(sendData);

  return (
    <main
      style={{
        flex: 1,
        display: "flex",
        justifyContent: "center",
        flexDirection: "column",
        alignItems: "center",
      }}
    >
      <MicrophoneVisualizer
        micStream={micStream}
        playbackStream={playbackStream}
      />
    </main>
  );
} 