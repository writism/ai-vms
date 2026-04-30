"use client";

import { useState } from "react";
import { Bell } from "lucide-react";
import { useNotification } from "../../application/hooks/useNotification";
import { cn } from "@/lib/utils";
import { formatTimestamp } from "../../../face/ui/lib/format-time";

const dangerTypeLabels: Record<string, string> = {
  FACE_RECOGNIZED: "얼굴 인식",
  FIRE: "화재",
  SMOKE: "연기",
  WEAPON: "무기",
  VIOLENCE: "폭력",
  FIGHT: "싸움",
  FALL: "쓰러짐",
  INTRUSION: "침입",
};

const severityColors: Record<string, string> = {
  LOW: "text-blue-500 dark:text-blue-400",
  MEDIUM: "text-amber-500 dark:text-amber-400",
  HIGH: "text-orange-500 dark:text-orange-400",
  CRITICAL: "text-red-500 dark:text-red-400",
};

export function NotificationBell() {
  const { notifications, unreadCount, markRead, markAllRead } = useNotification();
  const [open, setOpen] = useState(false);

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="relative rounded-md p-2 hover:bg-secondary"
      >
        <Bell className="h-[18px] w-[18px] text-muted-foreground" />
        {unreadCount > 0 && (
          <span className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white">
            {unreadCount > 99 ? "99+" : unreadCount}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 top-full z-50 mt-2 w-96 rounded-lg border bg-background shadow-lg">
          <div className="flex items-center justify-between border-b p-3">
            <span className="text-sm font-semibold">알림</span>
            {unreadCount > 0 && (
              <button
                onClick={markAllRead}
                className="text-xs text-muted-foreground hover:text-foreground"
              >
                모두 읽음
              </button>
            )}
          </div>
          <div className="max-h-96 overflow-y-auto">
            {notifications.length === 0 ? (
              <div className="p-4 text-center text-sm text-muted-foreground">
                알림이 없습니다
              </div>
            ) : (
              notifications.slice(0, 30).map((n) => {
                const label = dangerTypeLabels[n.danger_type] ?? n.danger_type;
                const severityClass = severityColors[n.severity] ?? "text-muted-foreground";
                return (
                  <div
                    key={n.id}
                    onClick={() => markRead(n.id)}
                    className={cn(
                      "cursor-pointer border-b p-3 text-sm hover:bg-secondary/50",
                      !n.read && "bg-secondary/20",
                    )}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className={cn("text-xs font-semibold", severityClass)}>
                        [{n.severity}] {label}
                      </span>
                      <span className="text-[10px] text-muted-foreground">
                        {formatTimestamp(n.created_at)}
                      </span>
                    </div>
                    {n.description && (
                      <p className="mt-1 text-sm">{n.description}</p>
                    )}
                    <p className="mt-1 font-mono text-[10px] text-muted-foreground">
                      cam: {n.camera_id.slice(0, 8)}
                    </p>
                  </div>
                );
              })
            )}
          </div>
        </div>
      )}
    </div>
  );
}
