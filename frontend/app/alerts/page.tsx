"use client";

import { useAtomValue } from "jotai";
import { useAlerts } from "@/features/alert/application/hooks/useAlerts";
import { severityColors, dangerLabels, dangerEventStatusLabels } from "@/lib/constants/labels";
import { cn } from "@/lib/utils";
import { ViewModeToggle } from "@/ui/components/ViewModeToggle";
import { viewModeAtom } from "@/features/preferences/application/atoms/viewModeAtom";

export default function AlertsPage() {
  const { events, total, isLoading } = useAlerts();
  const viewMode = useAtomValue(viewModeAtom);

  return (
    <div>
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-2xl font-semibold">알림</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            총 {total}건의 위험 이벤트
          </p>
        </div>
        <ViewModeToggle />
      </div>

      <div className={cn("mt-6", viewMode === "card" ? "space-y-3" : "space-y-1.5")}>
        {isLoading ? (
          <div className="flex h-48 items-center justify-center text-muted-foreground">
            로딩 중...
          </div>
        ) : events.length === 0 ? (
          <div className="flex h-48 items-center justify-center text-muted-foreground">
            감지된 이벤트가 없습니다
          </div>
        ) : viewMode === "card" ? (
          events.map((event) => (
            <div
              key={event.id}
              className="flex items-center justify-between rounded-lg border p-4"
            >
              <div className="flex items-center gap-4">
                <span
                  className={cn(
                    "rounded-full px-2 py-0.5 text-xs font-medium",
                    event.danger_type === "FACE_RECOGNIZED"
                      ? "bg-violet-100 text-violet-800"
                      : severityColors[event.severity],
                  )}
                >
                  {event.danger_type === "FACE_RECOGNIZED" ? "얼굴" : event.severity}
                </span>
                <div>
                  <p className="font-medium">
                    {dangerLabels[event.danger_type] ?? event.danger_type}
                  </p>
                  {event.description && (
                    <p className="text-sm text-muted-foreground">
                      {event.description}
                    </p>
                  )}
                  <p className="text-xs text-muted-foreground">
                    {new Date(event.created_at).toLocaleString("ko-KR")}
                  </p>
                </div>
              </div>
              <span className="text-sm text-muted-foreground">
                {dangerEventStatusLabels[event.status] ?? event.status}
              </span>
            </div>
          ))
        ) : (
          events.map((event) => (
            <div
              key={event.id}
              className="flex items-center gap-3 rounded-md border bg-card px-3 py-2 text-sm"
            >
              <span
                className={cn(
                  "shrink-0 rounded-full px-2 py-0.5 text-[11px] font-medium",
                  event.danger_type === "FACE_RECOGNIZED"
                    ? "bg-violet-100 text-violet-800"
                    : severityColors[event.severity],
                )}
              >
                {event.danger_type === "FACE_RECOGNIZED" ? "얼굴" : event.severity}
              </span>
              <span className="w-24 shrink-0 truncate font-medium">
                {dangerLabels[event.danger_type] ?? event.danger_type}
              </span>
              <span className="flex-1 truncate text-xs text-muted-foreground">
                {event.description ?? ""}
              </span>
              <span className="w-36 shrink-0 text-right text-[11px] text-muted-foreground">
                {new Date(event.created_at).toLocaleString("ko-KR", {
                  month: "2-digit",
                  day: "2-digit",
                  hour: "2-digit",
                  minute: "2-digit",
                  second: "2-digit",
                })}
              </span>
              <span className="w-12 shrink-0 text-right text-[11px] text-muted-foreground">
                {dangerEventStatusLabels[event.status] ?? event.status}
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
