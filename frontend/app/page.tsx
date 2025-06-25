"use client";

import React from "react";
import { useChatWebsocket } from "@/hooks/chat/useChatWebsocket";
import { useChatMicrophone } from "@/hooks/chat/useChatMicrophone";
import { BadgeHeader } from "@/components/header/BadgeHeader";
import { CenterContent } from "@/components/body/CenterContent";

export default function Page() {
  const { sendData, playbackStream, isConnected, isConnecting, error } =
  useChatWebsocket();
  const { micStream, isMicrophoneGranted, muted, toggleMute } = useChatMicrophone(sendData);

  return (
    <main
      style={{
        width: "100%",
        height: "100%",
        display: "flex",
        justifyContent: "center",
        flexDirection: "column",
        alignItems: "center",
      }}
    >
      <CenterContent micStream={micStream} playbackStream={playbackStream} muted={muted} />
      <BadgeHeader ws={{connected:isConnected,connecting:isConnecting,error:error?.toString()||null}} mic={{granted:isMicrophoneGranted,muted,onToggle:toggleMute}} />
    </main>
  );
} 