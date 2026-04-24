"use client";

import { useCallback, useState } from "react";
import type { MediaServerScanResult } from "@/features/stream/domain/model/mediaServer";
import { streamApi } from "@/features/stream/infrastructure/api/streamApi";

export function useMediaServers() {
  const [data, setData] = useState<MediaServerScanResult | null>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const scan = useCallback(async (subnet: string) => {
    setIsScanning(true);
    setError(null);
    try {
      const result = await streamApi.scanMediaServers(subnet);
      setData(result);
    } catch (e) {
      setError(e instanceof Error ? e.message : "스캔 실패");
    } finally {
      setIsScanning(false);
    }
  }, []);

  return { data, isScanning, error, scan };
}
