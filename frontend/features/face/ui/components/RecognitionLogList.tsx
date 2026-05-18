"use client";

import { memo, useCallback, useState } from "react";
import { useRecognitionLogs } from "../../application/hooks/useRecognitionLogs";
import { cn } from "@/lib/utils";
import { formatTimeOnly } from "../lib/format-time";
import {
  RecognitionDetailDialog,
  type RecognitionDetailData,
} from "./RecognitionDetailDialog";
import type { RecognitionLog } from "../../domain/model/face";

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

interface LogItemProps {
  log: RecognitionLog;
  onClick: (data: RecognitionDetailData) => void;
}

const LogItem = memo(function LogItem({ log, onClick }: LogItemProps) {
  const confPct = log.confidence > 1 ? log.confidence : log.confidence * 100;
  const handleClick = useCallback(() => {
    onClick({
      logId: log.id,
      title: log.identity_name,
      subtitle: typeLabels[log.identity_type] ?? log.identity_type,
      imageUrl: log.image_url ?? null,
      cameraId: log.camera_id,
      occurredAt: log.created_at,
      confidencePct: confPct,
      isRegistered: log.is_registered,
    });
  }, [log, onClick, confPct]);

  return (
    <button
      type="button"
      onClick={handleClick}
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
        <span className="text-xs">{formatTimeOnly(log.created_at)}</span>
      </div>
    </button>
  );
});

export function RecognitionLogList() {
  const { logs, isLoading, refresh } = useRecognitionLogs();
  const [detail, setDetail] = useState<RecognitionDetailData | null>(null);

  const handleOpen = useCallback((data: RecognitionDetailData) => {
    setDetail(data);
  }, []);

  const handleClose = useCallback(() => {
    setDetail(null);
  }, []);

  const handleAssigned = useCallback(() => {
    refresh?.();
    setDetail(null);
  }, [refresh]);

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
        {logs.map((log) => (
          <LogItem key={log.id} log={log} onClick={handleOpen} />
        ))}
      </div>

      <RecognitionDetailDialog
        open={detail !== null}
        onClose={handleClose}
        data={detail}
        onAssigned={handleAssigned}
      />
    </>
  );
}
