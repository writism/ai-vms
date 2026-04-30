"use client";

import { useState } from "react";
import { useRecognitionLogs } from "../../application/hooks/useRecognitionLogs";
import { cn } from "@/lib/utils";
import { formatTimeOnly } from "../lib/format-time";
import {
  RecognitionDetailDialog,
  type RecognitionDetailData,
} from "./RecognitionDetailDialog";

const typeLabels: Record<string, string> = {
  EMPLOYEE: "임직원",
  VISITOR: "방문객",
  UNKNOWN: "미등록",
};

const typeColors: Record<string, string> = {
  EMPLOYEE: "text-blue-400",
  VISITOR: "text-emerald-400",
  UNKNOWN: "text-yellow-400",
};

export function RecognitionLogList() {
  const { logs, isLoading, refresh } = useRecognitionLogs();
  const [detail, setDetail] = useState<RecognitionDetailData | null>(null);

  if (isLoading) {
    return (
      <div className="flex h-48 items-center justify-center text-muted-foreground">
        로딩 중...
      </div>
    );
  }

  if (logs.length === 0) {
    return (
      <div className="flex h-48 items-center justify-center text-muted-foreground">
        인식 로그 없음
      </div>
    );
  }

  return (
    <>
      <div className="space-y-2">
        {logs.map((log) => {
          const confPct =
            log.confidence > 1 ? log.confidence : log.confidence * 100;
          return (
            <button
              type="button"
              key={log.id}
              onClick={() =>
                setDetail({
                  logId: log.id,
                  title: log.identity_name,
                  subtitle: typeLabels[log.identity_type] ?? log.identity_type,
                  imageUrl: log.image_url ?? null,
                  cameraId: log.camera_id,
                  occurredAt: log.created_at,
                  confidencePct: confPct,
                  isRegistered: log.is_registered,
                })
              }
              className={cn(
                "flex w-full items-center justify-between rounded-lg border px-3 py-2 text-sm transition-colors hover:bg-secondary/40",
                log.is_registered
                  ? "border-border"
                  : "border-yellow-500/30 bg-yellow-500/5",
              )}
            >
              <div className="flex items-center gap-3">
                <span
                  className={cn(
                    "font-medium",
                    typeColors[log.identity_type] ?? "text-gray-400",
                  )}
                >
                  [{typeLabels[log.identity_type] ?? log.identity_type}]
                </span>
                <span className="font-semibold">{log.identity_name}</span>
              </div>
              <div className="flex items-center gap-3 text-muted-foreground">
                <span
                  className={cn(
                    "font-mono",
                    confPct >= 80
                      ? "text-green-400"
                      : confPct >= 60
                        ? "text-yellow-400"
                        : "text-red-400",
                  )}
                  title="일치도 (embedding 코사인 유사도)"
                >
                  {confPct.toFixed(1)}%
                </span>
                <span className="text-xs">
                  {formatTimeOnly(log.created_at)}
                </span>
              </div>
            </button>
          );
        })}
      </div>

      <RecognitionDetailDialog
        open={detail !== null}
        onClose={() => setDetail(null)}
        data={detail}
        onAssigned={() => {
          refresh?.();
          setDetail(null);
        }}
      />
    </>
  );
}
