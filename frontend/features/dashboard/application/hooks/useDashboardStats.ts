"use client";

import useSWR from "swr";
import type { Camera } from "@/features/camera/domain/model/camera";
import type { DangerEventList } from "@/features/alert/infrastructure/api/alertApi";
import type { EventList } from "@/features/event/infrastructure/api/eventApi";
import type { Identity } from "@/features/face/domain/model/face";

export function useDashboardStats() {
  const { data: cameras } = useSWR<Camera[]>("/api/cameras");
  const { data: alerts } = useSWR<DangerEventList>("/api/alerts/events?limit=5");
  const { data: events } = useSWR<EventList>("/api/events?limit=5");
  const { data: identities } = useSWR<Identity[]>("/api/faces/identities");

  const cameraStats = {
    total: cameras?.length ?? 0,
    online: cameras?.filter((c) => c.status === "ONLINE").length ?? 0,
    offline: cameras?.filter((c) => c.status === "OFFLINE").length ?? 0,
    error: cameras?.filter((c) => c.status === "ERROR").length ?? 0,
  };

  const alertStats = {
    total: alerts?.total ?? 0,
    pending: alerts?.items.filter((a) => a.status === "PENDING").length ?? 0,
    critical: alerts?.items.filter((a) => a.severity === "CRITICAL").length ?? 0,
  };

  const identityStats = {
    total: identities?.length ?? 0,
    internal: identities?.filter((i) => i.identity_type === "INTERNAL").length ?? 0,
    external: identities?.filter((i) => i.identity_type === "EXTERNAL").length ?? 0,
    vip: identities?.filter((i) => i.identity_type === "VIP").length ?? 0,
    blacklist: identities?.filter((i) => i.identity_type === "BLACKLIST").length ?? 0,
  };

  return {
    cameraStats,
    alertStats,
    identityStats,
    recentAlerts: alerts?.items ?? [],
    recentEvents: events?.items ?? [],
  };
}
