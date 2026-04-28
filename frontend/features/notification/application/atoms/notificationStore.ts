"use client";

import { atom, getDefaultStore } from "jotai";
import { env } from "@/infrastructure/config/env";

export interface DangerEventNotification {
  id: string;
  camera_id: string;
  danger_type: string;
  severity: string;
  confidence: number;
  description: string | null;
  snapshot_path: string | null;
  status: string;
  resolved_by: string | null;
  resolved_at: string | null;
  created_at: string;
  read: boolean;
}

export interface RecognitionNotification {
  id: string;
  camera_id: string;
  identity_id: string | null;
  identity_name: string;
  identity_type: string;
  confidence: number;
  is_registered: boolean;
  created_at: string;
}

const MAX_DANGER = 200;
const MAX_RECOG = 100;

export const dangerEventsAtom = atom<DangerEventNotification[]>([]);
export const recognitionEventsAtom = atom<RecognitionNotification[]>([]);
export const wsConnectedAtom = atom<boolean>(false);

const jotaiStore = typeof window !== "undefined" ? getDefaultStore() : null;

let initialized = false;
let ws: WebSocket | null = null;
let reconnectTimer: ReturnType<typeof setTimeout> | null = null;

function scheduleReconnect() {
  if (reconnectTimer) clearTimeout(reconnectTimer);
  reconnectTimer = setTimeout(connect, 3000);
}

function connect() {
  if (typeof window === "undefined") return;
  if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
    return;
  }
  try {
    ws = new WebSocket(`${env.wsUrl}/api/ws/notifications`);
  } catch {
    scheduleReconnect();
    return;
  }
  ws.onopen = () => {
    jotaiStore?.set(wsConnectedAtom, true);
  };
  ws.onclose = () => {
    jotaiStore?.set(wsConnectedAtom, false);
    scheduleReconnect();
  };
  ws.onerror = () => {
    ws?.close();
  };
  ws.onmessage = (event) => {
    if (!jotaiStore) return;
    try {
      const msg = JSON.parse(event.data);
      if (msg.type === "DANGER_EVENT" && msg.data?.id) {
        const incoming = { ...(msg.data as Omit<DangerEventNotification, "read">), read: false };
        const current = jotaiStore.get(dangerEventsAtom);
        if (current.some((e) => e.id === incoming.id)) return;
        jotaiStore.set(dangerEventsAtom, [incoming, ...current].slice(0, MAX_DANGER));
      } else if (msg.type === "recognition" && msg.data?.id) {
        const incoming = msg.data as RecognitionNotification;
        const current = jotaiStore.get(recognitionEventsAtom);
        if (current.some((e) => e.id === incoming.id)) return;
        jotaiStore.set(recognitionEventsAtom, [incoming, ...current].slice(0, MAX_RECOG));
      }
    } catch {
      // ignore malformed
    }
  };
}

export function ensureNotificationStream() {
  if (typeof window === "undefined") return;
  if (initialized) return;
  initialized = true;
  connect();
}

export function markDangerRead(id: string) {
  if (!jotaiStore) return;
  const list = jotaiStore.get(dangerEventsAtom);
  jotaiStore.set(
    dangerEventsAtom,
    list.map((e) => (e.id === id ? { ...e, read: true } : e)),
  );
}

export function markAllDangerRead() {
  if (!jotaiStore) return;
  const list = jotaiStore.get(dangerEventsAtom);
  jotaiStore.set(
    dangerEventsAtom,
    list.map((e) => ({ ...e, read: true })),
  );
}
