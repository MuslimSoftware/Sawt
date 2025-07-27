import React from 'react';
import { useChat, SystemState } from '@/contexts/ChatContext';
import styles from './SystemStatePill.module.css';
import { AudioLines, Diamond } from 'lucide-react';
import { colors } from '@/theme/colors';

type SystemStateConfig = {
  text: string;
  icon: React.ElementType;
  backgroundColor: string;
  color: string;
};

const systemStateConfig: Record<SystemState, SystemStateConfig> = {
  transcription_start: {
    text: 'Transcribing',
    icon: AudioLines,
    backgroundColor: colors.systemState.transcription_start,
    color: colors.text.primary,
  },
  get_agent_response_start: {
    text: 'Prompting',
    icon: AudioLines,
    backgroundColor: colors.systemState.get_agent_response_start,
    color: colors.text.primary,
  },
  tts_start: {
    text: 'Synthesizing',
    icon: AudioLines,
    backgroundColor: colors.systemState.tts_start,
    color: colors.text.primary,
  },
  idle: {
    text: 'Waiting',
    icon: Diamond,
    backgroundColor: colors.systemState.idle,
    color: colors.ui.backdrop,
  },
};

const SystemStatePill: React.FC = () => {
  const { systemState } = useChat();
  const { text, icon: Icon, backgroundColor, color } =
    systemStateConfig[systemState || 'idle'];

  const active = systemState !== 'idle';

  return (
    <div
      className={`${styles.pill} ${active ? styles.active : ''}`}
      style={{ backgroundColor, color }}
    >
      <Icon
        size={16}
        className={`${styles.icon} ${active ? styles.iconActive : ''}`}
      />
      <span>{text}</span>
    </div>
  );
};

export default SystemStatePill;
