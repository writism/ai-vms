"use client";

import { atom } from "jotai";
import { env } from "@/infrastructure/config/env";
import { jotaiStore } from "@/infrastructure/jotai/store";

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
    jotaiStore.set(wsConnectedAtom, true);
    console.debug("[notification] ws open");
  };
  ws.onclose = () => {
    jotaiStore.set(wsConnectedAtom, false);
    console.debug("[notification] ws close");
    scheduleReconnect();
  };
  ws.onerror = () => {
    ws?.close();
  };
  ws.onmessage = (event) => {
    try {
      const msg = JSON.parse(event.data);
      console.debug("[notification] received type=", msg?.type, "id=", msg?.data?.id);
      if (msg.type === "DANGER_EVENT" && msg.data?.id) {
        const incoming = { ...(msg.data as Omit<DangerEventNotification, "read">), read: false };
        const current = jotaiStore.get(dangerEventsAtom);
        if (current.some((e) => e.id === incoming.id)) return;
        const next = [incoming, ...current].slice(0, MAX_DANGER);
        jotaiStore.set(dangerEventsAtom, next);
        console.debug("[notification] danger atom set, count=", next.length);
      } else if (msg.type === "recognition" && msg.data?.id) {
        const incoming = msg.data as RecognitionNotification;
        const current = jotaiStore.get(recognitionEventsAtom);
        if (current.some((e) => e.id === incoming.id)) return;
        const next = [incoming, ...current].slice(0, MAX_RECOG);
        jotaiStore.set(recognitionEventsAtom, next);
        console.debug("[notification] recog atom set, count=", next.length);
      }
    } catch (e) {
      console.warn("[notification] malformed message", e);
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
  const list = jotaiStore.get(dangerEventsAtom);
  jotaiStore.set(
    dangerEventsAtom,
    list.map((e) => (e.id === id ? { ...e, read: true } : e)),
  );
}

export function markAllDangerRead() {
  const list = jotaiStore.get(dangerEventsAtom);
  jotaiStore.set(
    dangerEventsAtom,
    list.map((e) => ({ ...e, read: true })),
  );
}
