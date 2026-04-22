"use client";

import useSWR from "swr";
import type { Camera } from "../../domain/model/camera";

export function useCameras() {
  const { data, error, isLoading, mutate } = useSWR<Camera[]>("/api/cameras");

  return {
    cameras: data ?? [],
    isLoading,
    error,
    refresh: mutate,
  };
}
