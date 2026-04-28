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
  const missingPhoto = !identity.face_image_url;
  return (
    <div
      className={cn(
        "cursor-pointer rounded-lg border bg-card p-4 transition-colors hover:bg-muted/50",
        missingPhoto && "border-amber-300 dark:border-amber-800",
      )}
      onClick={onClick}
    >
      <div className="flex items-center gap-3">
        {identity.face_image_url ? (
          <img
            src={`${env.apiUrl}${identity.face_image_url}`}
            alt={identity.name}
            className="h-12 w-12 shrink-0 rounded-full border border-border object-cover"
          />
        ) : (
          <div className="relative">
            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full border border-amber-400 bg-muted text-lg font-semibold text-muted-foreground dark:border-amber-700">
              {identity.name.charAt(0)}
            </div>
            <span className="absolute -right-1 -bottom-1 rounded-full bg-amber-500 px-1.5 text-[9px] font-bold leading-4 text-white">
              !
            </span>
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
      {missingPhoto && (
        <p className="mt-2 text-xs text-amber-700 dark:text-amber-400">
          얼굴 사진이 없습니다 — 카드를 눌러 사진을 추가하세요
        </p>
      )}
    </div>
  );
}
