"use client";

import { useEffect, useMemo } from "react";
import useSWR from "swr";
import { useAtomValue } from "jotai";
import type { RecognitionLog } from "../../domain/model/face";
import {
  ensureNotificationStream,
  recognitionEventsAtom,
} from "@/features/notification/application/atoms/notificationStore";

export function useRecognitionLogs() {
  const { data, error, isLoading, mutate } = useSWR<RecognitionLog[]>(
    "/api/faces/recognition-logs?limit=20",
  );
  useEffect(() => {
    ensureNotificationStream();
  }, []);
  const realtime = useAtomValue(recognitionEventsAtom);

  const realtimeLogs: RecognitionLog[] = useMemo(
    () =>
      realtime.map((r) => ({
        id: r.id,
        camera_id: r.camera_id,
        identity_id: r.identity_id ?? null,
        identity_name: r.identity_name,
        identity_type: r.identity_type,
        confidence: r.confidence,
        is_registered: r.is_registered,
        image_url: (r as { image_url?: string | null }).image_url ?? null,
        created_at: r.created_at,
      })),
    [realtime],
  );

  const dedupedLogs = useMemo(() => {
    const allLogs = [...realtimeLogs, ...(data ?? [])];
    const seen = new Set<string>();
    return allLogs.filter((log) => {
      if (seen.has(log.id)) return false;
      seen.add(log.id);
      return true;
    });
  }, [realtimeLogs, data]);

  return {
    logs: dedupedLogs,
    isLoading,
    error,
    refresh: mutate,
  };
}
