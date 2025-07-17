"use client";

import React from "react";
import { colors, spacing, borderRadius, shadows } from "@/theme/colors";

interface Props {
  connected: boolean;
  connecting: boolean;
  error: string | null;
}

const pillStyle: React.CSSProperties = {
  padding: `${spacing.sm} ${spacing.xl}`,
  borderRadius: borderRadius.pill,
  fontSize: 14,
  fontWeight: 500,
  color: colors.text.secondary,
  boxShadow: shadows.sm,
  zIndex: 1000,
};

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
    <div style={{ ...pillStyle, background: bg }}>
      {text}
    </div>
  );
}; 