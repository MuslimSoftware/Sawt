"use client";

import { useChatWebsocket } from "@/hooks/chat/useChatWebsocket";
import { useChatMicrophone } from "@/hooks/chat/useChatMicrophone";
import React, {
    createContext,
    useContext,
    useState,
    ReactNode,
  } from 'react';
  
  export type Message = {
    role: 'user' | 'ai' | 'server';
    content: string;
  }

  export interface ChatContextType {
    messages: Message[];
    setMessages: React.Dispatch<React.SetStateAction<Message[]>>;
    isLoading: boolean;
    playbackStream: MediaStream | null;
    isConnected: boolean;
    isConnecting: boolean;
    error: string | null;
    micStream: MediaStream | null;
    isMicrophoneGranted: boolean;
    muted: boolean;
    toggleMute: () => void;
    systemState: SystemState | undefined;
  }

  export type SystemState = "transcription_start" | "get_agent_response_start" | "tts_start" | "idle";

  const ChatContext = createContext<ChatContextType | undefined>(undefined);
  
  export function ChatProvider({ children }: { children: ReactNode }) {
    const [messages, setMessages] = useState<Message[]>([]);
    const [systemState, setSystemState] = useState<SystemState>();
    const { sendData, playbackStream, isConnected, isConnecting, error, isLoading } = useChatWebsocket({setMessages, setSystemState});
    
    const { micStream, isMicrophoneGranted, muted, toggleMute } = useChatMicrophone({send: sendData});
    
    return <ChatContext.Provider value={{ 
      messages, 
      setMessages, 
      isLoading, 
      playbackStream, 
      isConnected, 
      isConnecting, 
      error,
      micStream,
      isMicrophoneGranted,
      muted,
      toggleMute,
      systemState
    }}>{children}</ChatContext.Provider>;
  }
  
  export function useChat() {
    const ctx = useContext(ChatContext);
    if (!ctx) {
      throw new Error('useChat must be used within a ChatProvider');
    }
    return ctx;
  }
  