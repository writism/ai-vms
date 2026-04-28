"use client";

import { useRecognitionLogs } from "../../application/hooks/useRecognitionLogs";
import { cn } from "@/lib/utils";

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
  const { logs, isLoading } = useRecognitionLogs();

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
    <div className="space-y-2">
      {logs.map((log) => (
        <div
          key={log.id}
          className={cn(
            "flex items-center justify-between rounded-lg border px-3 py-2 text-sm",
            log.is_registered ? "border-border" : "border-yellow-500/30 bg-yellow-500/5",
          )}
        >
          <div className="flex items-center gap-3">
            <span className={cn("font-medium", typeColors[log.identity_type] ?? "text-gray-400")}>
              [{typeLabels[log.identity_type] ?? log.identity_type}]
            </span>
            <span className="font-semibold">{log.identity_name}</span>
          </div>
          <div className="flex items-center gap-3 text-muted-foreground">
            <span className={cn(
              "font-mono",
              log.confidence >= 80 ? "text-green-400" : log.confidence >= 60 ? "text-yellow-400" : "text-red-400",
            )}>
              {log.confidence.toFixed(1)}%
            </span>
            <span className="text-xs">
              {new Date(log.created_at).toLocaleTimeString("ko-KR")}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}
