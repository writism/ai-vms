"use client";

import useSWR from "swr";
import type { Identity } from "../../domain/model/face";

export function useIdentities() {
  const { data, error, isLoading, mutate } = useSWR<Identity[]>("/api/faces/identities");

  return {
    identities: data ?? [],
    isLoading,
    error,
    refresh: mutate,
  };
}
