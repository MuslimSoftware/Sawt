"use client";
import React from "react";
import { WebsocketStatusPill } from "@/components/header/WebsocketStatusPill";
import { MicStatusBadge } from "@/components/header/MicStatusBadge";
import styles from "./BadgeHeader.module.css";

type Props = {
  ws: { connected: boolean; connecting: boolean; error: string | null };
  mic: { granted: boolean; muted: boolean; onToggle: () => void };
};

export const BadgeHeader: React.FC<Props> = ({ ws, mic }) => (
  <div className={styles.container}>
    <WebsocketStatusPill connected={ws.connected} connecting={ws.connecting} error={ws.error} />
    <MicStatusBadge granted={mic.granted} muted={mic.muted} onToggle={mic.onToggle} />
  </div>
); 