"use client";
import { useChat } from "@/contexts/ChatContext";
import React from "react";
import { WebsocketStatusPill } from "@/components/header/WebsocketStatusPill";
import { MicStatusBadge } from "@/components/header/MicStatusBadge";
import SystemStatePill from "./SystemStatePill";
import styles from "./BadgeHeader.module.css";

export const BadgeHeader: React.FC = () => {
  const { isConnected, isConnecting, error, isMicrophoneGranted, muted, toggleMute } = useChat();
  return (
    <div className={styles.container}>
      <div className={styles.row}>
        <WebsocketStatusPill connected={isConnected} connecting={isConnecting} error={error} />
        <MicStatusBadge granted={isMicrophoneGranted} muted={muted} onToggle={toggleMute} />
      </div>
      <div className={styles.row}>
        <SystemStatePill />
      </div>
    </div>
  );
} 