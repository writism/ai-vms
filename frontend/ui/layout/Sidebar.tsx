"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  Camera,
  Monitor,
  UserRound,
  Bell,
  SlidersHorizontal,
  CalendarClock,
  Settings,
  PanelLeftClose,
  PanelLeftOpen,
  type LucideIcon,
} from "lucide-react";

const navigation: { name: string; href: string; icon: LucideIcon }[] = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "카메라", href: "/cameras", icon: Camera },
  { name: "라이브뷰", href: "/live", icon: Monitor },
  { name: "출입관리", href: "/faces", icon: UserRound },
  { name: "알림", href: "/alerts", icon: Bell },
  { name: "알림 규칙", href: "/alerts/rules", icon: SlidersHorizontal },
  { name: "이벤트", href: "/events", icon: CalendarClock },
  { name: "설정", href: "/settings", icon: Settings },
];

export function Sidebar({ className }: { className?: string }) {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside
      className={cn(
        "flex h-full shrink-0 flex-col border-r bg-background transition-[width] duration-200",
        collapsed ? "w-[68px] min-w-[68px]" : "w-60 min-w-[240px] max-w-[240px]",
        className,
      )}
    >
      <div className="flex h-14 items-center justify-between border-b px-4">
        {!collapsed && <span className="text-lg font-bold">AI-VMS</span>}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className={cn(
            "rounded-md p-1 text-muted-foreground hover:bg-secondary hover:text-foreground",
            collapsed && "mx-auto",
          )}
        >
          {collapsed ? (
            <PanelLeftOpen className="h-[18px] w-[18px]" />
          ) : (
            <PanelLeftClose className="h-[18px] w-[18px]" />
          )}
        </button>
      </div>
      <nav className="flex-1 space-y-1 p-2">
        {navigation.map((item) => {
          const isActive =
            item.href === "/"
              ? pathname === "/"
              : pathname.startsWith(item.href);
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              title={collapsed ? item.name : undefined}
              className={cn(
                "relative flex h-9 items-center rounded-md text-sm font-medium transition-colors",
                collapsed ? "justify-center px-0" : "gap-3 px-3",
                isActive
                  ? "bg-secondary text-secondary-foreground"
                  : "text-muted-foreground hover:bg-secondary/50 hover:text-foreground",
              )}
            >
              {isActive && (
                <span className="absolute left-0 top-1 bottom-1 w-[3px] rounded-r-full bg-primary" />
              )}
              <Icon className="h-[18px] w-[18px] shrink-0" />
              {!collapsed && <span>{item.name}</span>}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
