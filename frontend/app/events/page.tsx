"use client";

import { useState } from "react";
import { useEvents } from "@/features/event/application/hooks/useEvents";
import type { EventItem } from "@/features/event/infrastructure/api/eventApi";

const typeLabels: Record<string, string> = {
  FACE_RECOGNIZED: "얼굴 인식",
  FACE_UNIDENTIFIED: "미식별 얼굴",
  DANGER_DETECTED: "위험 감지",
  CAMERA_ONLINE: "카메라 온라인",
  CAMERA_OFFLINE: "카메라 오프라인",
  ACCESS_GRANTED: "출입 허용",
  ACCESS_DENIED: "출입 거부",
};

const typeIcons: Record<string, string> = {
  FACE_RECOGNIZED: "인",
  FACE_UNIDENTIFIED: "?",
  DANGER_DETECTED: "!",
  CAMERA_ONLINE: "▶",
  CAMERA_OFFLINE: "■",
  ACCESS_GRANTED: "✓",
  ACCESS_DENIED: "✕",
};

const typeColors: Record<string, string> = {
  DANGER_DETECTED: "bg-red-100 text-red-800",
  FACE_UNIDENTIFIED: "bg-yellow-100 text-yellow-800",
  CAMERA_OFFLINE: "bg-gray-100 text-gray-800",
  ACCESS_DENIED: "bg-orange-100 text-orange-800",
};

function groupByDate(events: EventItem[]) {
  const groups: Record<string, EventItem[]> = {};
  for (const event of events) {
    const date = new Date(event.created_at).toLocaleDateString("ko-KR", {
      year: "numeric",
      month: "long",
      day: "numeric",
      weekday: "short",
    });
    if (!groups[date]) groups[date] = [];
    groups[date].push(event);
  }
  return groups;
}

export default function EventsPage() {
  const { events, total, isLoading } = useEvents();
  const [filter, setFilter] = useState<string>("ALL");

  const filteredEvents =
    filter === "ALL"
      ? events
      : events.filter((e) => e.event_type === filter);

  const grouped = groupByDate(filteredEvents);

  return (
    <div>
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold">이벤트 이력</h2>
          <p className="mt-1 text-sm text-muted-foreground">총 {total}건</p>
        </div>
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        {[
          { value: "ALL", label: "전체" },
          { value: "FACE_RECOGNIZED", label: "얼굴 인식" },
          { value: "DANGER_DETECTED", label: "위험 감지" },
          { value: "CAMERA_ONLINE", label: "카메라 온라인" },
          { value: "CAMERA_OFFLINE", label: "카메라 오프라인" },
        ].map((f) => (
          <button
            key={f.value}
            onClick={() => setFilter(f.value)}
            className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
              filter === f.value
                ? "bg-primary text-primary-foreground"
                : "bg-secondary text-secondary-foreground hover:bg-secondary/80"
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      <div className="mt-6">
        {isLoading ? (
          <div className="flex h-48 items-center justify-center text-muted-foreground">
            로딩 중...
          </div>
        ) : filteredEvents.length === 0 ? (
          <div className="flex h-48 items-center justify-center text-muted-foreground">
            이벤트가 없습니다
          </div>
        ) : (
          <div className="space-y-6">
            {Object.entries(grouped).map(([date, dayEvents]) => (
              <div key={date}>
                <h3 className="mb-2 text-sm font-medium text-muted-foreground">
                  {date}
                </h3>
                <div className="relative space-y-1 border-l-2 border-border pl-4">
                  {dayEvents.map((event) => (
                    <div
                      key={event.id}
                      className="relative flex items-center gap-3 rounded-lg p-2 hover:bg-secondary/30"
                    >
                      <div className="absolute -left-[1.375rem] h-2.5 w-2.5 rounded-full border-2 border-background bg-border" />
                      <div
                        className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs font-medium ${
                          typeColors[event.event_type] ?? "bg-blue-100 text-blue-800"
                        }`}
                      >
                        {typeIcons[event.event_type] ?? "·"}
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
                      <span className="shrink-0 text-xs text-muted-foreground">
                        {new Date(event.created_at).toLocaleTimeString("ko-KR", {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
