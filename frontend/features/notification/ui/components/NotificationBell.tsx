"use client";

import { useState } from "react";
import { Bell } from "lucide-react";
import { useNotification } from "../../application/hooks/useNotification";
import { cn } from "@/lib/utils";

export function NotificationBell() {
  const { notifications, unreadCount, markRead, markAllRead } =
    useNotification();
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
        <div className="absolute right-0 top-full z-50 mt-2 w-80 rounded-lg border bg-background shadow-lg">
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
          <div className="max-h-80 overflow-y-auto">
            {notifications.length === 0 ? (
              <div className="p-4 text-center text-sm text-muted-foreground">
                알림이 없습니다
              </div>
            ) : (
              notifications.slice(0, 20).map((n) => (
                <div
                  key={n.id}
                  onClick={() => markRead(n.id)}
                  className={cn(
                    "cursor-pointer border-b p-3 text-sm hover:bg-secondary/50",
                    !n.read && "bg-secondary/20",
                  )}
                >
                  <p className="font-medium">{n.type}</p>
                  <p className="mt-1 text-xs text-muted-foreground">
                    {new Date(n.timestamp).toLocaleTimeString("ko-KR")}
                  </p>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
