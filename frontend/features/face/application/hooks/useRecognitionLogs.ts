"use client";

import { useEffect, useState } from "react";
import useSWR from "swr";
import type { RecognitionLog } from "../../domain/model/face";
import { env } from "@/infrastructure/config/env";

export function useRecognitionLogs() {
  const { data, error, isLoading, mutate } = useSWR<RecognitionLog[]>(
    "/api/faces/recognition-logs?limit=20",
  );
  const [realtimeLogs, setRealtimeLogs] = useState<RecognitionLog[]>([]);

  useEffect(() => {
    const wsUrl = env.wsUrl || env.apiUrl.replace("http", "ws");
    const ws = new WebSocket(`${wsUrl}/api/ws/notifications`);

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === "recognition") {
          const log: RecognitionLog = {
            id: msg.data.id,
            camera_id: msg.data.camera_id,
            identity_id: msg.data.identity_id ?? null,
            identity_name: msg.data.identity_name,
            identity_type: msg.data.identity_type,
            confidence: msg.data.confidence,
            is_registered: msg.data.is_registered,
            created_at: msg.data.created_at,
          };
          setRealtimeLogs((prev) => [log, ...prev].slice(0, 50));
        }
      } catch {}
    };

    return () => ws.close();
  }, []);

  const allLogs = [...realtimeLogs, ...(data ?? [])];
  const seen = new Set<string>();
  const dedupedLogs = allLogs.filter((log) => {
    if (seen.has(log.id)) return false;
    seen.add(log.id);
    return true;
  });

  return {
    logs: dedupedLogs,
    isLoading,
    error,
    refresh: mutate,
  };
}
