"use client";

import { useAtom } from "jotai";
import { LayoutGrid, List } from "lucide-react";
import { viewModeAtom } from "@/features/preferences/application/atoms/viewModeAtom";
import { cn } from "@/lib/utils";

export function ViewModeToggle({ className }: { className?: string }) {
  const [mode, setMode] = useAtom(viewModeAtom);
  return (
    <div
      className={cn(
        "inline-flex items-center rounded-md border border-border bg-background p-0.5",
        className,
      )}
      role="group"
      aria-label="보기 모드"
    >
      <button
        type="button"
        onClick={() => setMode("card")}
        title="카드 보기"
        className={cn(
          "flex h-7 w-7 items-center justify-center rounded transition-colors",
          mode === "card"
            ? "bg-secondary text-secondary-foreground"
            : "text-muted-foreground hover:bg-secondary/50 hover:text-foreground",
        )}
      >
        <LayoutGrid className="h-4 w-4" />
      </button>
      <button
        type="button"
        onClick={() => setMode("list")}
        title="리스트 보기"
        className={cn(
          "flex h-7 w-7 items-center justify-center rounded transition-colors",
          mode === "list"
            ? "bg-secondary text-secondary-foreground"
            : "text-muted-foreground hover:bg-secondary/50 hover:text-foreground",
        )}
      >
        <List className="h-4 w-4" />
      </button>
    </div>
  );
}
