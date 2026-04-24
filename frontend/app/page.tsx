"use client";

import { useDashboardStats } from "@/features/dashboard/application/hooks/useDashboardStats";
import { MediaServerSection } from "@/features/dashboard/ui/components/MediaServerSection";
import { severityColors, dangerLabels, eventTypeLabels } from "@/lib/constants/labels";
import { cn } from "@/lib/utils";

function StatCard({
  title,
  value,
  subtitle,
  accent,
}: {
  title: string;
  value: number;
  subtitle?: string;
  accent?: string;
}) {
  return (
    <div className="rounded-lg border bg-card p-4">
      <p className="text-sm text-muted-foreground">{title}</p>
      <p className={cn("mt-1 text-3xl font-bold", accent)}>{value}</p>
      {subtitle && (
        <p className="mt-1 text-xs text-muted-foreground">{subtitle}</p>
      )}
    </div>
  );
}

export default function DashboardPage() {
  const {
    cameraStats,
    alertStats,
    identityStats,
    recentAlerts,
    recentEvents,
  } = useDashboardStats();

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold">Dashboard</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          실시간 모니터링 현황
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard
          title="카메라"
          value={cameraStats.total}
          subtitle={`온라인 ${cameraStats.online} · 오프라인 ${cameraStats.offline}`}
        />
        <StatCard
          title="위험 알림"
          value={alertStats.total}
          subtitle={`대기 ${alertStats.pending}건`}
          accent={alertStats.pending > 0 ? "text-red-600" : undefined}
        />
        <StatCard
          title="등록 인물"
          value={identityStats.total}
          subtitle={`내부 ${identityStats.internal} · 외부 ${identityStats.external}`}
        />
        <StatCard
          title="VIP / 블랙리스트"
          value={identityStats.vip + identityStats.blacklist}
          subtitle={`VIP ${identityStats.vip} · 블랙리스트 ${identityStats.blacklist}`}
          accent={identityStats.blacklist > 0 ? "text-orange-600" : undefined}
        />
      </div>

      {/* Recent Activity */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Recent Alerts */}
        <div className="rounded-lg border bg-card">
          <div className="border-b px-4 py-3">
            <h3 className="font-semibold">최근 위험 알림</h3>
          </div>
          <div className="divide-y">
            {recentAlerts.length === 0 ? (
              <div className="flex h-32 items-center justify-center text-sm text-muted-foreground">
                감지된 위험 이벤트 없음
              </div>
            ) : (
              recentAlerts.map((alert) => (
                <div
                  key={alert.id}
                  className="flex items-center gap-3 px-4 py-3"
                >
                  <span
                    className={cn(
                      "rounded-full px-2 py-0.5 text-xs font-medium",
                      severityColors[alert.severity],
                    )}
                  >
                    {alert.severity}
                  </span>
                  <div className="flex-1">
                    <p className="text-sm font-medium">
                      {dangerLabels[alert.danger_type] ?? alert.danger_type}
                    </p>
                  </div>
                  <span className="text-xs text-muted-foreground">
                    {new Date(alert.created_at).toLocaleString("ko-KR")}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Recent Events */}
        <div className="rounded-lg border bg-card">
          <div className="border-b px-4 py-3">
            <h3 className="font-semibold">최근 이벤트</h3>
          </div>
          <div className="divide-y">
            {recentEvents.length === 0 ? (
              <div className="flex h-32 items-center justify-center text-sm text-muted-foreground">
                이벤트 없음
              </div>
            ) : (
              recentEvents.map((event) => (
                <div
                  key={event.id}
                  className="flex items-center gap-3 px-4 py-3"
                >
                  <div className="flex h-7 w-7 items-center justify-center rounded-full bg-secondary text-xs">
                    {(eventTypeLabels[event.event_type] ?? "?")[0]}
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">
                      {eventTypeLabels[event.event_type] ?? event.event_type}
                    </p>
                    {event.description && (
                      <p className="text-xs text-muted-foreground">
                        {event.description}
                      </p>
                    )}
                  </div>
                  <span className="text-xs text-muted-foreground">
                    {new Date(event.created_at).toLocaleString("ko-KR")}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Media Server Monitoring */}
      <MediaServerSection />
    </div>
  );
}
