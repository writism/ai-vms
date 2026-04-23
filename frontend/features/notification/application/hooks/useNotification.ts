"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { env } from "@/infrastructure/config/env";

export interface Notification {
  id: string;
  type: string;
  data: Record<string, unknown>;
  timestamp: number;
  read: boolean;
}

export function useNotification() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    let ws: WebSocket | null = null;
    let timer: ReturnType<typeof setTimeout> | null = null;
    let unmounted = false;

    function connect() {
      if (unmounted) return;
      ws = new WebSocket(`${env.wsUrl}/api/ws/notifications`);
      wsRef.current = ws;

      ws.onopen = () => setConnected(true);

      ws.onclose = () => {
        setConnected(false);
        if (!unmounted) {
          timer = setTimeout(connect, 3000);
        }
      };

      ws.onerror = () => {
        ws?.close();
      };

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          const notification: Notification = {
            id: crypto.randomUUID(),
            type: msg.type,
            data: msg.data,
            timestamp: Date.now(),
            read: false,
          };
          setNotifications((prev) => [notification, ...prev].slice(0, 100));
        } catch {
          // ignore malformed messages
        }
      };
    }

    connect();

    return () => {
      unmounted = true;
      if (timer) clearTimeout(timer);
      ws?.close();
    };
  }, []);

  const markRead = useCallback((id: string) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, read: true } : n)),
    );
  }, []);

  const markAllRead = useCallback(() => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  }, []);

  const unreadCount = notifications.filter((n) => !n.read).length;

  return { notifications, unreadCount, connected, markRead, markAllRead };
}
