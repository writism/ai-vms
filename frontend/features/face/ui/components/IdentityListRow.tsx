"use client";

import type { Identity } from "../../domain/model/face";
import { cn } from "@/lib/utils";
import { env } from "@/infrastructure/config/env";

const typeLabels: Record<string, string> = {
  EMPLOYEE: "임직원",
  VISITOR: "방문객",
};

const typeColors: Record<string, string> = {
  EMPLOYEE: "bg-blue-100 text-blue-800",
  VISITOR: "bg-emerald-100 text-emerald-800",
};

export function IdentityListRow({ identity, onClick }: { identity: Identity; onClick?: () => void }) {
  return (
    <div
      onClick={onClick}
      className="flex cursor-pointer items-center gap-3 rounded-md border bg-card px-3 py-2 text-sm transition-colors hover:bg-secondary/40"
    >
      {identity.face_image_url ? (
        <img
          src={`${env.apiUrl}${identity.face_image_url}`}
          alt={identity.name}
          className="h-8 w-8 shrink-0 rounded-full border border-border object-cover"
        />
      ) : (
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-amber-400 bg-muted text-xs font-semibold text-muted-foreground">
          {identity.name.charAt(0)}
        </div>
      )}
      <span className="w-32 truncate font-semibold">{identity.name}</span>
      <span
        className={cn(
          "shrink-0 rounded-full px-2 py-0.5 text-[11px] font-medium",
          typeColors[identity.identity_type],
        )}
      >
        {typeLabels[identity.identity_type]}
      </span>
      <span className="flex-1 truncate text-xs text-muted-foreground">
        {identity.department && `부서: ${identity.department}  `}
        {identity.employee_id && `사번: ${identity.employee_id}  `}
        {identity.company && `소속: ${identity.company}  `}
        {identity.visit_purpose && `목적: ${identity.visit_purpose}`}
      </span>
    </div>
  );
}
