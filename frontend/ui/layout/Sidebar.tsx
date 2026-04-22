"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const navigation = [
  { name: "Dashboard", href: "/", icon: "📊" },
  { name: "카메라", href: "/cameras", icon: "📹" },
  { name: "라이브뷰", href: "/live", icon: "🖥" },
  { name: "인물관리", href: "/faces", icon: "👤" },
  { name: "알림", href: "/alerts", icon: "🔔" },
  { name: "알림 규칙", href: "/alerts/rules", icon: "📐" },
  { name: "이벤트", href: "/events", icon: "📋" },
  { name: "설정", href: "/settings", icon: "⚙" },
];

export function Sidebar({ className }: { className?: string }) {
  const pathname = usePathname();

  return (
    <aside
      className={cn(
        "flex h-full w-60 flex-col border-r bg-background",
        className,
      )}
    >
      <div className="flex h-14 items-center border-b px-4">
        <span className="text-lg font-bold">AI-VMS</span>
      </div>
      <nav className="flex-1 space-y-1 p-2">
        {navigation.map((item) => {
          const isActive =
            item.href === "/"
              ? pathname === "/"
              : pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-secondary text-secondary-foreground"
                  : "text-muted-foreground hover:bg-secondary/50 hover:text-foreground",
              )}
            >
              <span>{item.icon}</span>
              <span>{item.name}</span>
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
