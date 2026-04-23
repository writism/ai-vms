"use client";

import { useEffect, useState } from "react";
import { env } from "@/infrastructure/config/env";

export type ServiceStatus = "checking" | "connected" | "disconnected";

export interface ServiceHealth {
  api: ServiceStatus;
  go2rtc: ServiceStatus;
  turn: ServiceStatus;
}

async function checkHttp(url: string): Promise<boolean> {
  try {
    const res = await fetch(url, { method: "GET", signal: AbortSignal.timeout(3000) });
    return res.ok;
  } catch {
    return false;
  }
}

interface HealthResponse {
  services: { turn?: boolean };
}

export function useServiceHealth() {
  const [health, setHealth] = useState<ServiceHealth>({
    api: "checking",
    go2rtc: "checking",
    turn: "checking",
  });

  useEffect(() => {
    const check = async () => {
      const [apiOk, go2rtcOk] = await Promise.all([
        checkHttp(`${env.apiUrl}/api/cameras`),
        checkHttp(`${env.go2rtcUrl}/api/streams`),
      ]);

      let turnOk = false;
      try {
        const res = await fetch(`${env.apiUrl}/health`, { signal: AbortSignal.timeout(5000) });
        if (res.ok) {
          const data: HealthResponse = await res.json();
          turnOk = data.services.turn ?? false;
        }
      } catch {}

      setHealth({
        api: apiOk ? "connected" : "disconnected",
        go2rtc: go2rtcOk ? "connected" : "disconnected",
        turn: turnOk ? "connected" : "disconnected",
      });
    };
    check();
  }, []);

  return health;
}
