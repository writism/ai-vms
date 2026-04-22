"use client";

import type { Identity } from "../../domain/model/face";
import { cn } from "@/lib/utils";

const typeLabels: Record<string, string> = {
  INTERNAL: "내부인",
  EXTERNAL: "외부인",
  VIP: "VIP",
  BLACKLIST: "블랙리스트",
};

const typeColors: Record<string, string> = {
  INTERNAL: "bg-blue-100 text-blue-800",
  EXTERNAL: "bg-gray-100 text-gray-800",
  VIP: "bg-yellow-100 text-yellow-800",
  BLACKLIST: "bg-red-100 text-red-800",
};

export function IdentityCard({ identity }: { identity: Identity }) {
  return (
    <div className="rounded-lg border bg-card p-4">
      <div className="flex items-center justify-between">
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
      <div className="mt-2 space-y-1 text-sm text-muted-foreground">
        {identity.department && <p>부서: {identity.department}</p>}
        {identity.employee_id && <p>사번: {identity.employee_id}</p>}
      </div>
    </div>
  );
}
