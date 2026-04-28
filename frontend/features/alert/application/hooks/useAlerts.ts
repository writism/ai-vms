"use client";

import { useEffect } from "react";
import useSWR from "swr";
import { useAtomValue } from "jotai";
import type { DangerEvent, DangerEventList } from "../../infrastructure/api/alertApi";
import {
  dangerEventsAtom,
  ensureNotificationStream,
} from "@/features/notification/application/atoms/notificationStore";

export function useAlerts() {
  const { data, error, isLoading, mutate } = useSWR<DangerEventList>("/api/alerts/events");
  useEffect(() => {
    ensureNotificationStream();
  }, []);
  const realtime = useAtomValue(dangerEventsAtom);

  const realtimeEvents: DangerEvent[] = realtime.map((r) => ({
    id: r.id,
    camera_id: r.camera_id,
    danger_type: r.danger_type,
    severity: r.severity,
    confidence: r.confidence,
    description: r.description,
    snapshot_path: r.snapshot_path,
    status: r.status,
    resolved_by: r.resolved_by,
    resolved_at: r.resolved_at,
    created_at: r.created_at,
  }));

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
