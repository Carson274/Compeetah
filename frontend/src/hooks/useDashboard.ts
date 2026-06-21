import { useEffect, useRef, useState } from "react";
import { api, wsUrl } from "../api";
import type { Dashboard } from "../types";

interface State {
  data: Dashboard | null;
  connected: boolean;
}

/**
 * Subscribes to the live dashboard websocket and keeps the latest snapshot.
 * Falls back to a one-shot fetch on load, and auto-reconnects if the socket
 * drops (so the TV recovers on its own after a Pi/network blip).
 */
export function useDashboard(): State {
  const [data, setData] = useState<Dashboard | null>(null);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const retry = useRef<number | undefined>(undefined);

  useEffect(() => {
    let closed = false;

    // immediate paint from REST while the socket warms up
    api.dashboard().then(setData).catch(() => {});

    const connect = () => {
      const ws = new WebSocket(wsUrl());
      wsRef.current = ws;

      ws.onopen = () => setConnected(true);
      ws.onmessage = (ev) => {
        try {
          const msg = JSON.parse(ev.data);
          if (msg.type === "dashboard") setData(msg.data as Dashboard);
        } catch {
          /* ignore malformed frames */
        }
      };
      ws.onclose = () => {
        setConnected(false);
        if (!closed) retry.current = window.setTimeout(connect, 3000);
      };
      ws.onerror = () => ws.close();
    };

    connect();
    return () => {
      closed = true;
      window.clearTimeout(retry.current);
      wsRef.current?.close();
    };
  }, []);

  return { data, connected };
}
