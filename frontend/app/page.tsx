"use client";

import React from "react";
import { useChatWebsocket } from "@/hooks/chat/useChatWebsocket";
import { useChatMicrophone } from "@/hooks/chat/useChatMicrophone";
import { BadgeHeader } from "@/components/header/BadgeHeader";
import { CenterContent } from "@/components/body/CenterContent";
import { colors } from "@/theme/colors";

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
        position: "relative",
      }}
    >
      {/* Top fade overlay */}
      <div style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        height: "20%",
        background: `linear-gradient(to bottom, ${colors.background.primary}, transparent)`,
        zIndex: 10,
        pointerEvents: "none",
      }} />
      
      {/* Bottom fade overlay */}
      <div style={{
        position: "fixed",
        bottom: 0,
        left: 0,
        right: 0,
        height: "20%",
        background: `linear-gradient(to top, ${colors.background.primary}, transparent)`,
        zIndex: 10,
        pointerEvents: "none",
      }} />

      <CenterContent micStream={micStream} playbackStream={playbackStream} muted={muted} />
      <BadgeHeader ws={{connected:isConnected,connecting:isConnecting,error:error?.toString()||null}} mic={{granted:isMicrophoneGranted,muted,onToggle:toggleMute}} />
    </main>
  );
} 