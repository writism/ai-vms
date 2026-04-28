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

export function IdentityCard({ identity, onClick }: { identity: Identity; onClick?: () => void }) {
  return (
    <div className="cursor-pointer rounded-lg border bg-card p-4 transition-colors hover:bg-muted/50" onClick={onClick}>
      <div className="flex items-center gap-3">
        {identity.face_image_url ? (
          <img
            src={`${env.apiUrl}${identity.face_image_url}`}
            alt={identity.name}
            className="h-12 w-12 shrink-0 rounded-full border border-border object-cover"
          />
        ) : (
          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full border border-border bg-muted text-lg font-semibold text-muted-foreground">
            {identity.name.charAt(0)}
          </div>
        )}
        <div className="flex flex-1 items-center justify-between">
          <h3 className="font-semibold">{identity.name}</h3>
        <span
          className={cn(
            "rounded-full px-2 py-0.5 text-xs font-medium",
            typeColors[identity.identity_type],
          )}
        >
          {typeLabels[identity.identity_type]}
        </span>
        </div>
      </div>
      <div className="mt-2 space-y-1 text-sm text-muted-foreground">
        {identity.department && <p>부서: {identity.department}</p>}
        {identity.employee_id && <p>사번: {identity.employee_id}</p>}
        {identity.company && <p>소속: {identity.company}</p>}
        {identity.visit_purpose && <p>방문목적: {identity.visit_purpose}</p>}
      </div>
    </div>
  );
}
