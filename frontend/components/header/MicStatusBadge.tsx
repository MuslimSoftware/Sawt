"use client";

import React from "react";
import { Mic, MicOff, Ban } from 'lucide-react';

interface Props {
  granted: boolean;
  muted: boolean;
  onToggle: () => void;
}

const style: React.CSSProperties = {
  position: "relative",
  padding: "6px 14px",
  borderRadius: 9999,
  fontSize: 18,
  fontWeight: 500,
  color: "#fff",
  background: "rgba(255,255,255,0.15)",
  backdropFilter: "blur(6px)",
  boxShadow: "0 2px 6px rgba(0,0,0,0.15)",
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
  const bg = granted
    ? muted
      ? "rgba(220,53,69,0.4)"
      : "rgba(40,167,69,0.4)"
    : "rgba(108,117,125,0.5)"; // gray

  return (
    <div
      style={{ ...style, background: bg, cursor: granted ? "pointer" : "not-allowed" }}
      onClick={granted ? onToggle : undefined}
    >
      {icon}
    </div>
  );
}; 