"use client";

import useSWR from "swr";
import type { FaceSuggestion } from "../../infrastructure/api/faceApi";

export function useFaceSuggestions() {
  const { data, error, isLoading, mutate } = useSWR<FaceSuggestion[]>(
    "/api/faces/suggestions",
    { refreshInterval: 30000 },
  );
  return {
    suggestions: data ?? [],
    isLoading,
    error,
    refresh: mutate,
  };
}
