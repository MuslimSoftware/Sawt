"use client";

import React from "react";

interface Props {
  connected: boolean;
  connecting: boolean;
  error: string | null;
}

const pillStyle: React.CSSProperties = {

  padding: "6px 14px",
  borderRadius: 9999,
  fontSize: 14,
  fontWeight: 500,
  color: "#fff",
  boxShadow: "0 2px 6px rgba(0,0,0,0.15)",
  zIndex: 1000,
};

export const WebsocketStatusPill: React.FC<Props> = ({ connected, connecting, error }) => {
  let text = "Disconnected";
  let bg = "#dc3545"; // red

  if (connecting) {
    text = "Connecting…";
    bg = "rgba(255,193,7,0.4)"; // yellow
  } else if (connected) {
    text = "Connected";
    bg = "rgba(40,167,69,0.4)"; // green
  } else if (error) {
    text = "Error";
    bg = "rgba(220,53,69,0.4)"; // red
  }

  return (
    <div style={{ ...pillStyle, background: bg }}>
      {text}
    </div>
  );
}; 