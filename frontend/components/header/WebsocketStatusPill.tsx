"use client";

import React from "react";
import { colors } from "@/theme/colors";
import styles from "./WebsocketStatusPill.module.css";

interface Props {
  connected: boolean;
  connecting: boolean;
  error: string | null;
}

export const WebsocketStatusPill: React.FC<Props> = ({ connected, connecting, error }) => {
  let text = "Disconnected";
  let bg: string = colors.status.error;

  if (connecting) {
    text = "Connecting…";
    bg = colors.status.warning;
  } else if (connected) {
    text = "Connected";
    bg = colors.status.success;
  } else if (error) {
    text = "Error";
    bg = colors.status.error;
  }

  return (
    <div className={styles.pill} style={{ background: bg }}>
      {text}
    </div>
  );
}; 