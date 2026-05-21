"use client";

import { useState } from "react";
import { useAtomValue } from "jotai";
import { useEvents } from "@/features/event/application/hooks/useEvents";
import type { EventItem } from "@/features/event/infrastructure/api/eventApi";
import { useCameras } from "@/features/camera/application/hooks/useCameras";
import { ViewModeToggle } from "@/ui/components/ViewModeToggle";
import { viewModeAtom } from "@/features/preferences/application/atoms/viewModeAtom";
import { RecognitionLogList } from "@/features/face/ui/components/RecognitionLogList";
import { formatTimestamp } from "@/features/face/ui/lib/format-time";

const typeLabels: Record<string, string> = {
  FACE_RECOGNIZED: "등록 인물 인식",
  DANGER_DETECTED: "위험 감지",
  CAMERA_ONLINE: "카메라 온라인",
  CAMERA_OFFLINE: "카메라 오프라인",
  ACCESS_GRANTED: "출입 허용",
  ACCESS_DENIED: "출입 거부",
};

const typeIcons: Record<string, string> = {
  FACE_RECOGNIZED: "인",
  DANGER_DETECTED: "!",
  CAMERA_ONLINE: "▶",
  CAMERA_OFFLINE: "■",
  ACCESS_GRANTED: "✓",
  ACCESS_DENIED: "✕",
};

const typeColors: Record<string, string> = {
  FACE_RECOGNIZED: "bg-blue-100 text-blue-800",
  DANGER_DETECTED: "bg-red-100 text-red-800",
  CAMERA_ONLINE: "bg-green-100 text-green-800",
  CAMERA_OFFLINE: "bg-gray-100 text-gray-800",
  ACCESS_GRANTED: "bg-emerald-100 text-emerald-800",
  ACCESS_DENIED: "bg-orange-100 text-orange-800",
};

// events 테이블에서 표시할 타입 (FACE_UNIDENTIFIED 제외)
const VISIBLE_EVENT_TYPES = new Set([
  "FACE_RECOGNIZED",
  "DANGER_DETECTED",
  "CAMERA_ONLINE",
  "CAMERA_OFFLINE",
  "ACCESS_GRANTED",
  "ACCESS_DENIED",
]);

const FILTERS = [
  { value: "ALL", label: "전체" },
  { value: "FACE_LOG", label: "얼굴인식 로그" },
  { value: "FACE_RECOGNIZED", label: "등록 인물 인식" },
  { value: "DANGER_DETECTED", label: "위험 감지" },
  { value: "CAMERA_STATUS", label: "카메라 상태" },
];

function groupByDate(events: EventItem[]) {
  const groups: Record<string, EventItem[]> = {};
  for (const event of events) {
    const d = new Date(event.created_at);
    const date = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
    if (!groups[date]) groups[date] = [];
    groups[date].push(event);
  }
  return groups;
}

export default function EventsPage() {
  const { events, total, isLoading } = useEvents();
  const { cameras } = useCameras();
  const viewMode = useAtomValue(viewModeAtom);
  const [filter, setFilter] = useState<string>("ALL");

  const cameraMap = Object.fromEntries(cameras.map((c) => [c.id, c.name]));

  const isFaceLog = filter === "FACE_LOG";

  const visibleEvents = events.filter((e) => VISIBLE_EVENT_TYPES.has(e.event_type));

  const filteredEvents = isFaceLog
    ? []
    : filter === "ALL"
      ? visibleEvents
      : filter === "CAMERA_STATUS"
        ? visibleEvents.filter((e) => e.event_type === "CAMERA_ONLINE" || e.event_type === "CAMERA_OFFLINE")
        : visibleEvents.filter((e) => e.event_type === filter);

  const grouped = groupByDate(filteredEvents);

  return (
    <div>
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold">이벤트 이력</h2>
          {!isFaceLog && (
            <p className="mt-1 text-sm text-muted-foreground">총 {filteredEvents.length}건</p>
          )}
        </div>
        {!isFaceLog && <ViewModeToggle />}
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        {FILTERS.map((f) => (
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
        {isFaceLog ? (
          <RecognitionLogList />
        ) : isLoading ? (
          <div className="flex h-48 items-center justify-center text-muted-foreground">
            로딩 중...
          </div>
        ) : filteredEvents.length === 0 ? (
          <div className="flex h-48 items-center justify-center text-muted-foreground">
            이벤트가 없습니다
          </div>
        ) : viewMode === "card" ? (
          <div className="space-y-6">
            {Object.entries(grouped).map(([date, dayEvents]) => (
              <div key={date}>
                <h3 className="mb-2 text-sm font-medium text-muted-foreground">{date}</h3>
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
                          {event.camera_id && cameraMap[event.camera_id] && (
                            <span className="ml-1.5 text-xs font-normal text-muted-foreground">
                              — {cameraMap[event.camera_id]}
                            </span>
                          )}
                        </p>
                        {event.description && (
                          <p className="text-xs text-muted-foreground">{event.description}</p>
                        )}
                      </div>
                      <span className="shrink-0 font-mono text-xs text-muted-foreground">
                        {formatTimestamp(event.created_at)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-1.5">
            {filteredEvents.map((event) => (
              <div
                key={event.id}
                className="flex items-center gap-3 rounded-md border bg-card px-3 py-2 text-sm"
              >
                <div
                  className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-[11px] font-medium ${
                    typeColors[event.event_type] ?? "bg-blue-100 text-blue-800"
                  }`}
                >
                  {typeIcons[event.event_type] ?? "·"}
                </div>
                <span className="w-32 shrink-0 truncate font-medium">
                  {typeLabels[event.event_type] ?? event.event_type}
                </span>
                <span className="w-28 shrink-0 truncate text-xs text-muted-foreground">
                  {event.camera_id ? (cameraMap[event.camera_id] ?? event.camera_id.slice(0, 8)) : ""}
                </span>
                <span className="flex-1 truncate text-xs text-muted-foreground">
                  {event.description ?? ""}
                </span>
                <span className="shrink-0 font-mono text-[11px] text-muted-foreground">
                  {formatTimestamp(event.created_at)}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
