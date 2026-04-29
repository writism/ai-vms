"use client";

import Link from "next/link";
import type { Camera } from "../../domain/model/camera";
import { cameraStatusColors, cameraStatusLabels } from "@/lib/constants/labels";
import { cn } from "@/lib/utils";

export function CameraListRow({ camera }: { camera: Camera }) {
  return (
    <Link
      href={`/cameras/${camera.id}`}
      className="flex items-center gap-4 rounded-md border bg-card px-3 py-2 text-sm transition-colors hover:bg-secondary/40"
    >
      <span className={cn("h-2 w-2 shrink-0 rounded-full", cameraStatusColors[camera.status])} />
      <span className="w-44 truncate font-semibold">{camera.name}</span>
      <span className="w-32 truncate font-mono text-xs text-muted-foreground">{camera.ip_address}</span>
      <span className="flex-1 truncate text-xs text-muted-foreground">
        {camera.manufacturer ?? ""}
        {camera.model ? ` ${camera.model}` : ""}
      </span>
      <span className="w-16 text-right text-xs text-muted-foreground">
        {cameraStatusLabels[camera.status]}
      </span>
    </Link>
  );
}
