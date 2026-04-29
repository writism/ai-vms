"use client";

import { useEffect } from "react";
import { Button } from "@/components/ui/button";
import { env } from "@/infrastructure/config/env";
import { cn } from "@/lib/utils";

export interface RecognitionDetailData {
  title: string;
  subtitle?: string | null;
  imageUrl: string | null;
  cameraId?: string | null;
  occurredAt: string;
  confidencePct: number;
  isRegistered?: boolean;
  extras?: { label: string; value: string }[];
}

const typeBadgeColors: Record<string, string> = {
  EMPLOYEE: "bg-blue-100 text-blue-800",
  VISITOR: "bg-emerald-100 text-emerald-800",
  UNKNOWN: "bg-yellow-100 text-yellow-800",
};

export function RecognitionDetailDialog({
  open,
  onClose,
  data,
}: {
  open: boolean;
  onClose: () => void;
  data: RecognitionDetailData | null;
}) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open || !data) return null;

  const fullSrc = data.imageUrl
    ? data.imageUrl.startsWith("http")
      ? data.imageUrl
      : `${env.apiUrl}${data.imageUrl}`
    : null;
  const occurred = new Date(data.occurredAt).toLocaleString("ko-KR");
  const camera = data.cameraId ? data.cameraId.slice(0, 8) : "-";

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="w-full max-w-md rounded-xl border border-border bg-card p-5 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-start justify-between gap-2">
          <div>
            <h2 className="text-lg font-semibold">{data.title}</h2>
            {data.subtitle && (
              <p className="mt-0.5 text-xs text-muted-foreground">{data.subtitle}</p>
            )}
          </div>
          <Button variant="ghost" size="sm" onClick={onClose}>
            닫기
          </Button>
        </div>

        <div className="mt-4 overflow-hidden rounded-lg border border-border bg-muted">
          {fullSrc ? (
            <img
              src={fullSrc}
              alt={data.title}
              className="block max-h-[60vh] w-full object-contain"
            />
          ) : (
            <div className="flex h-48 items-center justify-center text-sm text-muted-foreground">
              스냅샷 없음
            </div>
          )}
        </div>

        <dl className="mt-4 space-y-1.5 text-sm">
          <div className="flex justify-between">
            <dt className="text-muted-foreground">신뢰도</dt>
            <dd
              className={cn(
                "font-mono",
                data.confidencePct >= 80
                  ? "text-green-500"
                  : data.confidencePct >= 60
                    ? "text-yellow-500"
                    : "text-red-500",
              )}
            >
              {data.confidencePct.toFixed(1)}%
            </dd>
          </div>
          <div className="flex justify-between">
            <dt className="text-muted-foreground">시각</dt>
            <dd className="font-mono text-xs">{occurred}</dd>
          </div>
          <div className="flex justify-between">
            <dt className="text-muted-foreground">카메라</dt>
            <dd className="font-mono text-xs">{camera}</dd>
          </div>
          {data.isRegistered !== undefined && (
            <div className="flex justify-between">
              <dt className="text-muted-foreground">상태</dt>
              <dd>
                <span
                  className={cn(
                    "rounded-full px-2 py-0.5 text-xs font-medium",
                    data.isRegistered
                      ? typeBadgeColors.EMPLOYEE
                      : typeBadgeColors.UNKNOWN,
                  )}
                >
                  {data.isRegistered ? "등록 인물" : "미등록"}
                </span>
              </dd>
            </div>
          )}
          {data.extras?.map((ex) => (
            <div key={ex.label} className="flex justify-between">
              <dt className="text-muted-foreground">{ex.label}</dt>
              <dd className="text-xs">{ex.value}</dd>
            </div>
          ))}
        </dl>
      </div>
    </div>
  );
}
