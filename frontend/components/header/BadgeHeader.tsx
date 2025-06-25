"use client";
import React from "react";
import { WebsocketStatusPill } from "@/components/header/WebsocketStatusPill";
import { MicStatusBadge } from "@/components/header/MicStatusBadge";

type Props = {
  ws: { connected: boolean; connecting: boolean; error: string | null };
  mic: { granted: boolean; muted: boolean; onToggle: () => void };
};

export const BadgeHeader: React.FC<Props> = ({ ws, mic }) => (
  <div style={{position:'fixed',top:10,width:'100%',display:'flex',flexDirection:'row',justifyContent:'center',alignItems:'center',gap:12,zIndex:1000}}>
    <WebsocketStatusPill connected={ws.connected} connecting={ws.connecting} error={ws.error} />
    <MicStatusBadge granted={mic.granted} muted={mic.muted} onToggle={mic.onToggle} />
  </div>
); 