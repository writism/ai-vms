"use client";

import { useState, useCallback } from "react";
import { useAlertRules } from "@/features/alert/application/hooks/useAlertRules";
import { useServiceHealth, type ServiceStatus } from "@/features/stream/application/hooks/useServiceHealth";
import { useSettings, parseValue } from "@/features/setting/application/hooks/useSettings";
import type { SettingItem, SettingUpdateItem } from "@/features/setting/domain/model/setting";
import { env } from "@/infrastructure/config/env";

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between border-b py-3 last:border-b-0">
      <span className="text-sm text-muted-foreground">{label}</span>
      <span className="text-sm font-mono">{value}</span>
    </div>
  );
}

const statusConfig: Record<ServiceStatus, { color: string; label: string }> = {
  checking: { color: "bg-gray-400", label: "확인 중" },
  connected: { color: "bg-green-500", label: "연결됨" },
  warn: { color: "bg-yellow-400", label: "인증서 미승인" },
  disconnected: { color: "bg-red-500", label: "연결 실패" },
};

function StatusRow({ label, value, status }: { label: string; value: string; status: ServiceStatus }) {
  const cfg = statusConfig[status];
  return (
    <div className="flex items-center justify-between border-b py-3 last:border-b-0">
      <span className="text-sm text-muted-foreground">{label}</span>
      <div className="flex items-center gap-2">
        <span className="text-sm font-mono">{value}</span>
        <span className={`inline-block h-2.5 w-2.5 rounded-full ${cfg.color}`} title={cfg.label} />
      </div>
    </div>
  );
}

interface SettingRowProps {
  item: SettingItem;
  localValue: string;
  onChange: (key: string, value: string) => void;
}

function SettingRow({ item, localValue, onChange }: SettingRowProps) {
  if (item.type === "bool") {
    return (
      <div className="flex items-center justify-between border-b py-3 last:border-b-0">
        <span className="text-sm text-muted-foreground">{item.label}</span>
        <button
          type="button"
          onClick={() => onChange(item.key, localValue === "true" ? "false" : "true")}
          className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors ${
            localValue === "true" ? "bg-primary" : "bg-secondary"
          }`}
        >
          <span
            className={`pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow ring-0 transition ${
              localValue === "true" ? "translate-x-4" : "translate-x-0"
            }`}
          />
        </button>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-between border-b py-3 last:border-b-0">
      <span className="text-sm text-muted-foreground">{item.label}</span>
      <input
        type="number"
        step={item.type === "float" ? "0.01" : "1"}
        value={localValue}
        onChange={(e) => onChange(item.key, e.target.value)}
        className="w-28 rounded border bg-background px-2 py-1 text-right text-sm font-mono focus:outline-none focus:ring-1 focus:ring-primary"
      />
    </div>
  );
}

interface SettingsSectionProps {
  title: string;
  items: SettingItem[];
  localValues: Record<string, string>;
  onChange: (key: string, value: string) => void;
  onSave: (items: SettingItem[]) => void;
  saving: boolean;
}

function SettingsSection({ title, items, localValues, onChange, onSave, saving }: SettingsSectionProps) {
  const isDirty = items.some((item) => localValues[item.key] !== item.value);

  return (
    <div className="rounded-lg border bg-card">
      <div className="flex items-center justify-between border-b px-4 py-3">
        <h3 className="font-semibold">{title}</h3>
        {isDirty && (
          <button
            type="button"
            onClick={() => onSave(items)}
            disabled={saving}
            className="rounded bg-primary px-3 py-1 text-xs font-medium text-primary-foreground disabled:opacity-50"
          >
            {saving ? "저장 중..." : "저장"}
          </button>
        )}
      </div>
      <div className="px-4">
        {items.map((item) => (
          <SettingRow
            key={item.key}
            item={item}
            localValue={localValues[item.key] ?? item.value}
            onChange={onChange}
          />
        ))}
      </div>
    </div>
  );
}

export default function SettingsPage() {
  const { rules, isLoading: rulesLoading } = useAlertRules();
  const health = useServiceHealth();
  const { settings, isLoading: settingsLoading, saving, updateSettings } = useSettings();

  const [localValues, setLocalValues] = useState<Record<string, string>>({});

  const handleChange = useCallback((key: string, value: string) => {
    setLocalValues((prev) => ({ ...prev, [key]: value }));
  }, []);

  const handleSave = useCallback(
    async (items: SettingItem[]) => {
      const updates: SettingUpdateItem[] = items
        .filter((item) => (localValues[item.key] ?? item.value) !== item.value)
        .map((item) => ({
          key: item.key,
          value: parseValue(item, localValues[item.key] ?? item.value),
        }));
      if (updates.length === 0) return;
      await updateSettings(updates);
      setLocalValues((prev) => {
        const next = { ...prev };
        updates.forEach((u) => delete next[u.key]);
        return next;
      });
    },
    [localValues, updateSettings],
  );

  const getLocal = (items: SettingItem[]) =>
    Object.fromEntries(
      items.map((item) => [item.key, localValues[item.key] ?? item.value]),
    );

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold">시스템 설정</h2>
        <p className="mt-1 text-sm text-muted-foreground">환경 설정 및 연결 상태</p>
      </div>

      {/* Connection Status */}
      <div className="rounded-lg border bg-card">
        <div className="border-b px-4 py-3">
          <h3 className="font-semibold">연결 상태</h3>
        </div>
        <div className="px-4">
          <StatusRow label="API 서버" value={env.apiUrl} status={health.api} />
          <StatusRow label="WebSocket" value={env.wsUrl} status={health.api} />
          <StatusRow label="go2rtc 스트리밍" value={env.go2rtcUrl} status={health.go2rtc} />
          <StatusRow label="TURN 서버" value={env.turnUrl} status={health.turn} />
        </div>
      </div>

      {/* AI Settings */}
      {settingsLoading ? (
        <div className="flex h-24 items-center justify-center text-sm text-muted-foreground rounded-lg border bg-card">
          설정 로딩 중...
        </div>
      ) : settings ? (
        <>
          <SettingsSection
            title="얼굴 인식"
            items={settings.recognition}
            localValues={getLocal(settings.recognition)}
            onChange={handleChange}
            onSave={handleSave}
            saving={saving}
          />
          <SettingsSection
            title="클러스터링"
            items={settings.clustering}
            localValues={getLocal(settings.clustering)}
            onChange={handleChange}
            onSave={handleSave}
            saving={saving}
          />
          <SettingsSection
            title="파이프라인"
            items={settings.pipeline}
            localValues={getLocal(settings.pipeline)}
            onChange={handleChange}
            onSave={handleSave}
            saving={saving}
          />
        </>
      ) : null}

      {/* Alert Rules */}
      <div className="rounded-lg border bg-card">
        <div className="border-b px-4 py-3">
          <h3 className="font-semibold">알림 규칙</h3>
        </div>
        <div className="px-4">
          {rulesLoading ? (
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
                      최소 심각도: {rule.min_severity} · 유형: {rule.danger_types.join(", ")}
                    </p>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    {rule.notify_websocket && <span className="rounded bg-secondary px-1.5 py-0.5">WS</span>}
                    {rule.notify_mqtt && <span className="rounded bg-secondary px-1.5 py-0.5">MQTT</span>}
                    {rule.notify_email && <span className="rounded bg-secondary px-1.5 py-0.5">Email</span>}
                    <span className={rule.is_active ? "text-green-600" : "text-muted-foreground"}>
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
