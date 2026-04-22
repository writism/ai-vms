"use client";

import { useAlerts } from "@/features/alert/application/hooks/useAlerts";
import { cn } from "@/lib/utils";

const severityColors: Record<string, string> = {
  LOW: "bg-blue-100 text-blue-800",
  MEDIUM: "bg-yellow-100 text-yellow-800",
  HIGH: "bg-orange-100 text-orange-800",
  CRITICAL: "bg-red-100 text-red-800",
};

const statusLabels: Record<string, string> = {
  PENDING: "대기",
  ACKNOWLEDGED: "확인됨",
  RESOLVED: "처리완료",
  FALSE_ALARM: "오탐",
};

const dangerLabels: Record<string, string> = {
  FIRE: "화재",
  SMOKE: "연기",
  VIOLENCE: "폭력",
  FIGHT: "싸움",
  WEAPON: "무기",
  FALL: "쓰러짐",
  INTRUSION: "침입",
};

export default function AlertsPage() {
  const { events, total, isLoading } = useAlerts();

  return (
    <div>
      <div>
        <h2 className="text-2xl font-semibold">알림</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          총 {total}건의 위험 이벤트
        </p>
      </div>

      <div className="mt-6 space-y-3">
        {isLoading ? (
          <div className="flex h-48 items-center justify-center text-muted-foreground">
            로딩 중...
          </div>
        ) : events.length === 0 ? (
          <div className="flex h-48 items-center justify-center text-muted-foreground">
            감지된 이벤트가 없습니다
          </div>
        ) : (
          events.map((event) => (
            <div
              key={event.id}
              className="flex items-center justify-between rounded-lg border p-4"
            >
              <div className="flex items-center gap-4">
                <span
                  className={cn(
                    "rounded-full px-2 py-0.5 text-xs font-medium",
                    severityColors[event.severity],
                  )}
                >
                  {event.severity}
                </span>
                <div>
                  <p className="font-medium">
                    {dangerLabels[event.danger_type] ?? event.danger_type}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {new Date(event.created_at).toLocaleString("ko-KR")}
                  </p>
                </div>
              </div>
              <span className="text-sm text-muted-foreground">
                {statusLabels[event.status] ?? event.status}
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
