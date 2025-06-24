"use client";

import React, {
    createContext,
    useContext,
    useState,
    ReactNode,
  } from 'react';
  
  export interface ChatContextType {
    messages: string[];
    setMessages: (messages: string[]) => void;
  }

  const ChatContext = createContext<ChatContextType | undefined>(undefined);
  
  export function ChatProvider({ children }: { children: ReactNode }) {
    const [messages, setMessages] = useState<string[]>([]);
    
    return <ChatContext.Provider value={{ messages, setMessages }}>{children}</ChatContext.Provider>;
  }
  
  export function useChat() {
    const ctx = useContext(ChatContext);
    if (!ctx) {
      throw new Error('useChat must be used within a ChatProvider');
    }
    return ctx;
  }
  