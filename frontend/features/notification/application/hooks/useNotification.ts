"use client";

import { useAtomValue } from "jotai";
import { useEffect } from "react";
import {
  type DangerEventNotification,
  dangerEventsAtom,
  ensureNotificationStream,
  markAllDangerRead,
  markDangerRead,
  wsConnectedAtom,
} from "@/features/notification/application/atoms/notificationStore";

export type Notification = DangerEventNotification;

const EXCLUDED_FROM_BELL = new Set(["FACE_RECOGNIZED", "FACE_UNIDENTIFIED"]);

export function useNotification() {
  useEffect(() => {
    ensureNotificationStream();
  }, []);
  const events = useAtomValue(dangerEventsAtom);
  const connected = useAtomValue(wsConnectedAtom);
  const notifications = events.filter((e) => !EXCLUDED_FROM_BELL.has(e.danger_type));
  const unreadCount = notifications.filter((e) => !e.read).length;
  return {
    notifications,
    unreadCount,
    connected,
    markRead: markDangerRead,
    markAllRead: markAllDangerRead,
  };
}
