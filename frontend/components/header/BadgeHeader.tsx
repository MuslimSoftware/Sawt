"use client";
import { useChat } from "@/contexts/ChatContext";
import React from "react";
import { WebsocketStatusPill } from "@/components/header/WebsocketStatusPill";
import { MicStatusBadge } from "@/components/header/MicStatusBadge";
import styles from "./BadgeHeader.module.css";

export const BadgeHeader: React.FC = () => {
  const { isConnected, isConnecting, error, isMicrophoneGranted, muted, toggleMute } = useChat();
  return (
    <div className={styles.container}>
      <WebsocketStatusPill connected={isConnected} connecting={isConnecting} error={error} />
      <MicStatusBadge granted={isMicrophoneGranted} muted={muted} onToggle={toggleMute} />
    </div>
  );
} 