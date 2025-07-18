"use client";

import React from "react";
import { Mic, MicOff, Ban } from 'lucide-react';
import { colors } from "@/theme/colors";
import styles from "./MicStatusBadge.module.css";

interface Props {
  granted: boolean;
  muted: boolean;
  onToggle: () => void;
}

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
      className={`${styles.badge} ${granted ? '' : styles.notGranted}`}
      style={{ background: bg }}
      onClick={granted ? onToggle : undefined}
    >
      {icon}
    </div>
  );
}; 