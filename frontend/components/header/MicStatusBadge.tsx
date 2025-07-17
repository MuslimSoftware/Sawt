"use client";

import React from "react";
import { Mic, MicOff, Ban } from 'lucide-react';
import { colors, spacing, borderRadius, shadows } from "@/theme/colors";

interface Props {
  granted: boolean;
  muted: boolean;
  onToggle: () => void;
}

const style: React.CSSProperties = {
  position: "relative",
  padding: `${spacing.sm} ${spacing.xl}`,
  borderRadius: borderRadius.pill,
  fontSize: 18,
  fontWeight: 500,
  color: colors.text.secondary,
  background: colors.ui.backdrop,
  backdropFilter: "blur(6px)",
  boxShadow: shadows.sm,
  cursor: "pointer",
  userSelect: "none",
  zIndex: 1000,
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
};

const iconSize = 18;

export const MicStatusBadge: React.FC<Props> = ({ granted, muted, onToggle }) => {
  const icon = granted ? (muted ? <MicOff size={iconSize}/> : <Mic size={iconSize}/> ) : <Ban size={iconSize}/>;
  const bg: string = granted
    ? muted
      ? colors.status.error
      : colors.status.success
    : colors.status.disabled;

  return (
    <div
      style={{ ...style, background: bg, cursor: granted ? "pointer" : "not-allowed" }}
      onClick={granted ? onToggle : undefined}
    >
      {icon}
    </div>
  );
}; 