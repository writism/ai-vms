"use client";

import { useEvents } from "@/features/event/application/hooks/useEvents";

const typeLabels: Record<string, string> = {
  FACE_RECOGNIZED: "얼굴 인식",
  FACE_UNIDENTIFIED: "미식별 얼굴",
  DANGER_DETECTED: "위험 감지",
  CAMERA_ONLINE: "카메라 온라인",
  CAMERA_OFFLINE: "카메라 오프라인",
  ACCESS_GRANTED: "출입 허용",
  ACCESS_DENIED: "출입 거부",
};

export default function EventsPage() {
  const { events, total, isLoading } = useEvents();

  return (
    <div>
      <div>
        <h2 className="text-2xl font-semibold">이벤트 이력</h2>
        <p className="mt-1 text-sm text-muted-foreground">총 {total}건</p>
      </div>

      <div className="mt-6">
        {isLoading ? (
          <div className="flex h-48 items-center justify-center text-muted-foreground">
            로딩 중...
          </div>
        ) : events.length === 0 ? (
          <div className="flex h-48 items-center justify-center text-muted-foreground">
            이벤트가 없습니다
          </div>
        ) : (
          <div className="space-y-2">
            {events.map((event) => (
              <div
                key={event.id}
                className="flex items-center gap-4 rounded-lg border p-3"
              >
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-secondary text-xs">
                  {typeLabels[event.event_type]?.[0] ?? "?"}
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium">
                    {typeLabels[event.event_type] ?? event.event_type}
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
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
