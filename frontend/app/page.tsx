"use client";

import React from "react";
import { useChatWebsocket } from "@/hooks/chat/useChatWebsocket";
import { useChatMicrophone } from "@/hooks/chat/useChatMicrophone";
import { BadgeHeader } from "@/components/header/BadgeHeader";
import { CenterContent } from "@/components/body/CenterContent";
import styles from "./page.module.css";

export default function Page() {
  const { sendData, playbackStream, isConnected, isConnecting, error } =
  useChatWebsocket();
  const { micStream, isMicrophoneGranted, muted, toggleMute } = useChatMicrophone(sendData);

  return (
    <main className={styles.main}>
      {/* Top fade overlay */}
      <div className={styles.topFade} />
      
      {/* Bottom fade overlay */}
      <div className={styles.bottomFade} />

      <CenterContent micStream={micStream} playbackStream={playbackStream} muted={muted} />
      <BadgeHeader ws={{connected:isConnected,connecting:isConnecting,error:error?.toString()||null}} mic={{granted:isMicrophoneGranted,muted,onToggle:toggleMute}} />
    </main>
  );
} 