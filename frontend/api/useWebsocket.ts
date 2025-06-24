import { useState, useEffect, useCallback, useRef } from "react";

interface UseWebSocketOptions {
  url: string;
  onMessage: (event: MessageEvent) => void;
}

export const useWebSocket = ({ url, onMessage }: UseWebSocketOptions) => {
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    setIsConnecting(true);
    setError(null);
    const wsInstance = new WebSocket(url);
    wsInstance.binaryType = 'arraybuffer';

    wsInstance.onopen = () => {
      setIsConnected(true);
      setIsConnecting(false);
    };
    
    wsInstance.onclose = () => {
      setIsConnected(false);
      setIsConnecting(false);
    };

    wsInstance.onerror = (event: Event) => {
      setError(new Error("WebSocket connection error"));
      setIsConnected(false);
      setIsConnecting(false);
    };

    wsInstance.onmessage = (event: MessageEvent) => {
      onMessage(event);
    };

    ws.current = wsInstance;

    return () => {
      if (wsInstance.readyState === WebSocket.OPEN) {
        wsInstance.close();
      } else {
        // let the browser GC handle sockets that never opened to avoid spurious warnings
        wsInstance.onopen = null;
        wsInstance.onmessage = null;
        wsInstance.onclose = null;
        wsInstance.onerror = null;
      }
      ws.current = null;
      setIsConnected(false);
      setIsConnecting(false);
    };
  }, [url, onMessage]);

  const sendData = useCallback((data: string | ArrayBuffer) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(data);
    } else {
      console.error("[useWebSocket] WebSocket is not connected", ws.current?.readyState);
    }
  }, []);

  return { isConnected, isConnecting, error, sendData };
};