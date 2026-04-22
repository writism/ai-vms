"use client";

import { NotificationBell } from "@/features/notification/ui/components/NotificationBell";

export function Navbar() {
  return (
    <header className="flex h-14 items-center justify-between border-b bg-background px-6">
      <h1 className="text-sm font-medium text-muted-foreground">
        AI Multi-Agent 영상 관리/관제 시스템
      </h1>
      <div className="flex items-center gap-4">
        <NotificationBell />
        <span className="text-sm text-muted-foreground">관리자</span>
      </div>
    </header>
  );
}
