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
  }

  const ChatContext = createContext<ChatContextType | undefined>(undefined);
  
  export function ChatProvider({ children }: { children: ReactNode }) {
    const [messages, setMessages] = useState<Message[]>([]);
    const { sendData, playbackStream, isConnected, isConnecting, error, isLoading } = useChatWebsocket({setMessages});
    
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
      toggleMute
    }}>{children}</ChatContext.Provider>;
  }
  
  export function useChat() {
    const ctx = useContext(ChatContext);
    if (!ctx) {
      throw new Error('useChat must be used within a ChatProvider');
    }
    return ctx;
  }
  