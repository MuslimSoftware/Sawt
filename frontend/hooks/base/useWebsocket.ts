"use client";

import { useEffect, useReducer, useRef, useCallback } from "react";

type State = { connecting: boolean; connected: boolean; error: string | null };
const initial: State = { connecting: false, connected: false, error: null };

type Act =
  | { type: "connecting" }
  | { type: "open" }
  | { type: "close" }
  | { type: "error"; msg: string };

const reducer = (s: State, a: Act): State => {
  switch (a.type) {
    case "connecting":
      return { connecting: true, connected: false, error: null };
    case "open":
      return { connecting: false, connected: true, error: null };
    case "close":
      return { connecting: false, connected: false, error: null };
    case "error":
      return { connecting: false, connected: false, error: a.msg };
  }
};

export const useWebsocket = (
  url: string,
  onMessage: (e: MessageEvent) => void,
) => {
  const [{ connected, connecting, error }, dispatch] = useReducer(
    reducer,
    initial,
  );
  const wsRef = useRef<WebSocket | null>(null);

  const sendData = useCallback((data: string | ArrayBuffer) => {
    if (wsRef.current?.readyState !== WebSocket.OPEN) {
      return;
    }
    
    wsRef.current.send(data);
  }, []);

  useEffect(() => {
    dispatch({ type: "connecting" });
    const ws = new WebSocket(url);
    ws.binaryType = "arraybuffer";

    ws.onopen = () => dispatch({ type: "open" });
    ws.onclose = () => dispatch({ type: "close" });
    ws.onerror = (e: ErrorEvent) => dispatch({ type: "error", msg: e.message });
    ws.onmessage = onMessage;

    wsRef.current = ws;
    return () => {
      ws.close();
      wsRef.current = null;
    };
  }, [url]);

  return { sendData, isConnected: connected, isConnecting: connecting, error } as const;
};