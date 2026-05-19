"use client";

import { useEffect, useState } from "react";
import { env } from "@/infrastructure/config/env";

export type ServiceStatus = "checking" | "connected" | "warn" | "disconnected";

export interface ServiceHealth {
  api: ServiceStatus;
  go2rtc: ServiceStatus;
  turn: ServiceStatus;
}

type CheckResult = "connected" | "warn" | "disconnected";

async function checkHttp(url: string): Promise<CheckResult> {
  try {
    const res = await fetch(url, { method: "GET", signal: AbortSignal.timeout(3000) });
    return res.ok ? "connected" : "disconnected";
  } catch (e) {
    // TypeError = network/SSL error (server reachable but cert untrusted, or CORS preflight blocked)
    if (e instanceof TypeError) return "warn";
    return "disconnected";
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
      const [apiStatus, go2rtcStatus] = await Promise.all([
        checkHttp(`${env.apiUrl}/api/cameras`),
        checkHttp(`${env.go2rtcUrl}/api/streams`),
      ]);

      let turnStatus: CheckResult = "disconnected";
      try {
        const res = await fetch(`${env.apiUrl}/health`, { signal: AbortSignal.timeout(5000) });
        if (res.ok) {
          const data: HealthResponse = await res.json();
          turnStatus = data.services.turn ? "connected" : "disconnected";
        }
      } catch (e) {
        if (e instanceof TypeError) turnStatus = "warn";
      }

      setHealth({
        api: apiStatus,
        go2rtc: go2rtcStatus,
        turn: turnStatus,
      });
    };
    check();
  }, []);

  return health;
}
