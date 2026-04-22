"use client";

import { NotificationBell } from "@/features/notification/ui/components/NotificationBell";
import { useAuth } from "@/features/auth/application/hooks/useAuth";

export function Navbar() {
  const { user, logout } = useAuth();

  return (
    <header className="flex h-14 items-center justify-between border-b bg-background px-6">
      <h1 className="text-sm font-medium text-muted-foreground">
        AI Multi-Agent 영상 관리/관제 시스템
      </h1>
      <div className="flex items-center gap-4">
        <NotificationBell />
        <span className="text-sm text-muted-foreground">
          {user?.name ?? "관리자"}
        </span>
        <button
          onClick={logout}
          className="rounded-md px-2 py-1 text-xs text-muted-foreground hover:bg-secondary"
        >
          로그아웃
        </button>
      </div>
    </header>
  );
}
