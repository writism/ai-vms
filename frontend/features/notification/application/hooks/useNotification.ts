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

export function useNotification() {
  useEffect(() => {
    ensureNotificationStream();
  }, []);
  const events = useAtomValue(dangerEventsAtom);
  const connected = useAtomValue(wsConnectedAtom);
  const unreadCount = events.filter((e) => !e.read).length;
  return {
    notifications: events,
    unreadCount,
    connected,
    markRead: markDangerRead,
    markAllRead: markAllDangerRead,
  };
}
