"use client";

import { VideoPlayer } from "./VideoPlayer";
import { cn } from "@/lib/utils";

type GridLayout = 1 | 4 | 9 | 16;

export interface StreamSlot {
  name: string;
  rtspUrl?: string | null;
}

const gridClasses: Record<GridLayout, string> = {
  1: "grid-cols-1",
  4: "grid-cols-2",
  9: "grid-cols-3",
  16: "grid-cols-4",
};

export function MultiView({
  streams,
  layout = 4,
  className,
}: {
  streams: StreamSlot[];
  layout?: GridLayout;
  className?: string;
}) {
  const slots = Array.from({ length: layout }, (_, i) => streams[i] ?? null);

  return (
    <div className={cn("grid gap-1", gridClasses[layout], className)}>
      {slots.map((slot, i) => (
        <div key={i} className="aspect-video">
          {slot ? (
            <VideoPlayer streamName={slot.name} rtspUrl={slot.rtspUrl} className="h-full w-full" />
          ) : (
            <div className="flex h-full w-full items-center justify-center rounded-lg bg-muted text-muted-foreground">
              비어 있음
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
