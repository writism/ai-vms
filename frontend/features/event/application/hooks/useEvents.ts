"use client";

import useSWR from "swr";
import type { EventList } from "../../infrastructure/api/eventApi";

export function useEvents() {
  const { data, error, isLoading, mutate } = useSWR<EventList>("/api/events");

  return {
    events: data?.items ?? [],
    total: data?.total ?? 0,
    isLoading,
    error,
    refresh: mutate,
  };
}
