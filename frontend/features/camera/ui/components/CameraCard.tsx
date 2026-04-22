"use client";

import Link from "next/link";
import type { Camera } from "../../domain/model/camera";
import { cn } from "@/lib/utils";

const statusColors = {
  ONLINE: "bg-green-500",
  OFFLINE: "bg-gray-400",
  ERROR: "bg-red-500",
} as const;

const statusLabels = {
  ONLINE: "온라인",
  OFFLINE: "오프라인",
  ERROR: "에러",
} as const;

export function CameraCard({ camera }: { camera: Camera }) {
  return (
    <Link
      href={`/cameras/${camera.id}`}
      className="block rounded-lg border bg-card p-4 transition-shadow hover:shadow-md"
    >
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">{camera.name}</h3>
        <div className="flex items-center gap-2">
          <span
            className={cn("h-2 w-2 rounded-full", statusColors[camera.status])}
          />
          <span className="text-xs text-muted-foreground">
            {statusLabels[camera.status]}
          </span>
        </div>
      </div>
      <div className="mt-2 space-y-1 text-sm text-muted-foreground">
        <p>{camera.ip_address}</p>
        {camera.manufacturer && (
          <p>
            {camera.manufacturer}
            {camera.model ? ` ${camera.model}` : ""}
          </p>
        )}
      </div>
    </Link>
  );
}
