"use client";

import useSWR from "swr";
import type { DangerEventList } from "../../infrastructure/api/alertApi";

export function useAlerts() {
  const { data, error, isLoading, mutate } = useSWR<DangerEventList>("/api/alerts/events");

  return {
    events: data?.items ?? [],
    total: data?.total ?? 0,
    isLoading,
    error,
    refresh: mutate,
  };
}
