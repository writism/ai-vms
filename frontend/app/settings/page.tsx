"use client";

import { useAlertRules } from "@/features/alert/application/hooks/useAlertRules";
import { env } from "@/infrastructure/config/env";

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between border-b py-3 last:border-b-0">
      <span className="text-sm text-muted-foreground">{label}</span>
      <span className="text-sm font-mono">{value}</span>
    </div>
  );
}

export default function SettingsPage() {
  const { rules, isLoading } = useAlertRules();

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold">시스템 설정</h2>
        <p className="mt-1 text-sm text-muted-foreground">환경 설정 및 연결 상태</p>
      </div>

      {/* Connection Settings */}
      <div className="rounded-lg border bg-card">
        <div className="border-b px-4 py-3">
          <h3 className="font-semibold">연결 설정</h3>
        </div>
        <div className="px-4">
          <InfoRow label="API 서버" value={env.apiUrl} />
          <InfoRow label="WebSocket" value={env.wsUrl} />
          <InfoRow label="go2rtc 서버" value={env.go2rtcUrl} />
        </div>
      </div>

      {/* Alert Rules */}
      <div className="rounded-lg border bg-card">
        <div className="border-b px-4 py-3">
          <h3 className="font-semibold">알림 규칙</h3>
        </div>
        <div className="px-4">
          {isLoading ? (
            <div className="flex h-24 items-center justify-center text-sm text-muted-foreground">
              로딩 중...
            </div>
          ) : rules.length === 0 ? (
            <div className="flex h-24 items-center justify-center text-sm text-muted-foreground">
              설정된 알림 규칙이 없습니다
            </div>
          ) : (
            <div className="divide-y">
              {rules.map((rule) => (
                <div key={rule.id} className="flex items-center justify-between py-3">
                  <div>
                    <p className="text-sm font-medium">{rule.name}</p>
                    <p className="text-xs text-muted-foreground">
                      최소 심각도: {rule.min_severity} · 유형:{" "}
                      {rule.danger_types.join(", ")}
                    </p>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    {rule.notify_websocket && (
                      <span className="rounded bg-secondary px-1.5 py-0.5">WS</span>
                    )}
                    {rule.notify_mqtt && (
                      <span className="rounded bg-secondary px-1.5 py-0.5">MQTT</span>
                    )}
                    {rule.notify_email && (
                      <span className="rounded bg-secondary px-1.5 py-0.5">Email</span>
                    )}
                    <span
                      className={
                        rule.is_active
                          ? "text-green-600"
                          : "text-muted-foreground"
                      }
                    >
                      {rule.is_active ? "활성" : "비활성"}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* System Info */}
      <div className="rounded-lg border bg-card">
        <div className="border-b px-4 py-3">
          <h3 className="font-semibold">시스템 정보</h3>
        </div>
        <div className="px-4">
          <InfoRow label="버전" value="0.1.0" />
          <InfoRow label="프레임워크" value="Next.js + FastAPI" />
          <InfoRow label="AI 엔진" value="InsightFace + YOLO11" />
        </div>
      </div>
    </div>
  );
}
