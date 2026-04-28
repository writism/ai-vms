"use client";

import { useEffect, useState } from "react";
import useSWR from "swr";
import type { DangerEvent, DangerEventList } from "../../infrastructure/api/alertApi";
import { env } from "@/infrastructure/config/env";

export function useAlerts() {
  const { data, error, isLoading, mutate } = useSWR<DangerEventList>("/api/alerts/events");
  const [realtimeEvents, setRealtimeEvents] = useState<DangerEvent[]>([]);

  useEffect(() => {
    const wsUrl = env.wsUrl || env.apiUrl.replace("http", "ws");
    const ws = new WebSocket(`${wsUrl}/api/ws/notifications`);

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === "DANGER_EVENT") {
          setRealtimeEvents((prev) => [msg.data as DangerEvent, ...prev].slice(0, 50));
        }
      } catch {}
    };

    return () => ws.close();
  }, []);

  const allEvents = [...realtimeEvents, ...(data?.items ?? [])];
  const seen = new Set<string>();
  const dedupedEvents = allEvents.filter((e) => {
    if (seen.has(e.id)) return false;
    seen.add(e.id);
    return true;
  });

  return {
    events: dedupedEvents,
    total: (data?.total ?? 0) + realtimeEvents.length,
    isLoading,
    error,
    refresh: mutate,
  };
}
