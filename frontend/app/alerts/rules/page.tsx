"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { useAlertRules } from "@/features/alert/application/hooks/useAlertRules";
import { alertApi } from "@/features/alert/infrastructure/api/alertApi";

const DANGER_TYPES = [
  { value: "FIRE", label: "화재" },
  { value: "SMOKE", label: "연기" },
  { value: "VIOLENCE", label: "폭력" },
  { value: "FIGHT", label: "싸움" },
  { value: "WEAPON", label: "무기" },
  { value: "FALL", label: "쓰러짐" },
  { value: "INTRUSION", label: "침입" },
];

const SEVERITIES = ["LOW", "MEDIUM", "HIGH", "CRITICAL"];

export default function AlertRulesPage() {
  const { rules, isLoading, refresh } = useAlertRules();
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState("");
  const [selectedTypes, setSelectedTypes] = useState<string[]>([]);
  const [minSeverity, setMinSeverity] = useState("HIGH");
  const [channels, setChannels] = useState<string[]>(["WEBSOCKET"]);
  const [enableFaceRecognition, setEnableFaceRecognition] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const toggleType = (type: string) => {
    setSelectedTypes((prev) =>
      prev.includes(type) ? prev.filter((t) => t !== type) : [...prev, type],
    );
  };

  const toggleChannel = (ch: string) => {
    setChannels((prev) =>
      prev.includes(ch) ? prev.filter((c) => c !== ch) : [...prev, ch],
    );
  };

  const handleCreate = async () => {
    if (!name || (selectedTypes.length === 0 && !enableFaceRecognition)) return;
    setSubmitting(true);
    try {
      await alertApi.createRule({
        name,
        danger_types: selectedTypes,
        min_severity: minSeverity,
        notify_websocket: channels.includes("WEBSOCKET"),
        notify_mqtt: channels.includes("MQTT"),
        notify_email: channels.includes("EMAIL"),
        email_recipients: [],
        enable_face_recognition: enableFaceRecognition,
      });
      setShowForm(false);
      setName("");
      setSelectedTypes([]);
      setEnableFaceRecognition(false);
      refresh();
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (ruleId: string) => {
    await alertApi.deleteRule(ruleId);
    refresh();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold">알림 규칙</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            {rules.length}개 규칙
          </p>
        </div>
        <Button onClick={() => setShowForm(!showForm)}>
          {showForm ? "취소" : "규칙 추가"}
        </Button>
      </div>

      {showForm && (
        <div className="space-y-4 rounded-lg border bg-card p-4">
          <div>
            <label className="text-sm font-medium">규칙 이름</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm"
              placeholder="예: 화재 알림"
            />
          </div>

          <div>
            <label className="text-sm font-medium">위험 유형</label>
            <div className="mt-1 flex flex-wrap gap-2">
              {DANGER_TYPES.map((dt) => (
                <button
                  key={dt.value}
                  type="button"
                  onClick={() => toggleType(dt.value)}
                  className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
                    selectedTypes.includes(dt.value)
                      ? "bg-primary text-primary-foreground"
                      : "bg-secondary text-secondary-foreground"
                  }`}
                >
                  {dt.label}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="text-sm font-medium">얼굴 인식</label>
            <div className="mt-1">
              <button
                type="button"
                onClick={() => setEnableFaceRecognition(!enableFaceRecognition)}
                className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
                  enableFaceRecognition
                    ? "bg-primary text-primary-foreground"
                    : "bg-secondary text-secondary-foreground"
                }`}
              >
                얼굴 검색
              </button>
              <p className="mt-1 text-xs text-muted-foreground">
                등록된 인물이 카메라에서 인식되면 알림을 발생시킵니다
              </p>
            </div>
          </div>

          <div>
            <label className="text-sm font-medium">최소 심각도</label>
            <div className="mt-1 flex gap-2">
              {SEVERITIES.map((s) => (
                <button
                  key={s}
                  type="button"
                  onClick={() => setMinSeverity(s)}
                  className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
                    minSeverity === s
                      ? "bg-primary text-primary-foreground"
                      : "bg-secondary text-secondary-foreground"
                  }`}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="text-sm font-medium">알림 채널</label>
            <div className="mt-1 flex gap-2">
              {["WEBSOCKET", "MQTT", "EMAIL"].map((ch) => (
                <button
                  key={ch}
                  type="button"
                  onClick={() => toggleChannel(ch)}
                  className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
                    channels.includes(ch)
                      ? "bg-primary text-primary-foreground"
                      : "bg-secondary text-secondary-foreground"
                  }`}
                >
                  {ch}
                </button>
              ))}
            </div>
          </div>

          <Button onClick={handleCreate} disabled={submitting || !name || (selectedTypes.length === 0 && !enableFaceRecognition)}>
            {submitting ? "생성 중..." : "규칙 생성"}
          </Button>
        </div>
      )}

      <div className="space-y-3">
        {isLoading ? (
          <div className="flex h-48 items-center justify-center text-muted-foreground">
            로딩 중...
          </div>
        ) : rules.length === 0 ? (
          <div className="flex h-48 items-center justify-center text-muted-foreground">
            설정된 규칙이 없습니다
          </div>
        ) : (
          rules.map((rule) => (
            <div
              key={rule.id}
              className="flex items-center justify-between rounded-lg border p-4"
            >
              <div>
                <p className="font-medium">{rule.name}</p>
                <div className="mt-1 flex flex-wrap gap-1">
                  {rule.danger_types.map((dt) => (
                    <span
                      key={dt}
                      className="rounded bg-secondary px-1.5 py-0.5 text-xs"
                    >
                      {DANGER_TYPES.find((d) => d.value === dt)?.label ?? dt}
                    </span>
                  ))}
                  {rule.enable_face_recognition && (
                    <span className="rounded bg-violet-500/20 px-1.5 py-0.5 text-xs text-violet-400">
                      얼굴 검색
                    </span>
                  )}
                </div>
                <p className="mt-1 text-xs text-muted-foreground">
                  최소 심각도: {rule.min_severity} ·{" "}
                  {[
                    rule.notify_websocket && "WS",
                    rule.notify_mqtt && "MQTT",
                    rule.notify_email && "Email",
                  ]
                    .filter(Boolean)
                    .join(", ")}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <span
                  className={`text-xs ${
                    rule.is_active ? "text-green-600" : "text-muted-foreground"
                  }`}
                >
                  {rule.is_active ? "활성" : "비활성"}
                </span>
                <Button
                  size="sm"
                  variant="ghost"
                  className="text-red-500 hover:text-red-700"
                  onClick={() => handleDelete(rule.id)}
                >
                  삭제
                </Button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
