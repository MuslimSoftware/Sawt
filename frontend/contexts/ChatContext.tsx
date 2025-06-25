"use client";

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
  }

  const ChatContext = createContext<ChatContextType | undefined>(undefined);
  
  export function ChatProvider({ children }: { children: ReactNode }) {
    const [messages, setMessages] = useState<Message[]>([]);
    
    return <ChatContext.Provider value={{ messages, setMessages }}>{children}</ChatContext.Provider>;
  }
  
  export function useChat() {
    const ctx = useContext(ChatContext);
    if (!ctx) {
      throw new Error('useChat must be used within a ChatProvider');
    }
    return ctx;
  }
  