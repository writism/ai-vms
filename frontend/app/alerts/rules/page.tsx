"use client";

import { useState } from "react";
import { useAtomValue } from "jotai";
import { Button } from "@/components/ui/button";
import { useAlertRules, type AlertRule } from "@/features/alert/application/hooks/useAlertRules";
import { alertApi } from "@/features/alert/infrastructure/api/alertApi";
import { useCameras } from "@/features/camera/application/hooks/useCameras";
import { ViewModeToggle } from "@/ui/components/ViewModeToggle";
import { viewModeAtom } from "@/features/preferences/application/atoms/viewModeAtom";

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

interface RuleFormState {
  name: string;
  cameraId: string;
  selectedTypes: string[];
  minSeverity: string;
  channels: string[];
  enableFaceRecognition: boolean;
}

function emptyForm(): RuleFormState {
  return {
    name: "",
    cameraId: "",
    selectedTypes: [],
    minSeverity: "HIGH",
    channels: ["WEBSOCKET"],
    enableFaceRecognition: false,
  };
}

function ruleToForm(rule: AlertRule): RuleFormState {
  const channels: string[] = [];
  if (rule.notify_websocket) channels.push("WEBSOCKET");
  if (rule.notify_mqtt) channels.push("MQTT");
  if (rule.notify_email) channels.push("EMAIL");
  return {
    name: rule.name,
    cameraId: rule.camera_id ?? "",
    selectedTypes: [...rule.danger_types],
    minSeverity: rule.min_severity,
    channels,
    enableFaceRecognition: rule.enable_face_recognition,
  };
}

function RuleForm({
  initial,
  cameras,
  submitLabel,
  onSubmit,
  onCancel,
}: {
  initial: RuleFormState;
  cameras: { id: string; name: string; ip_address: string }[];
  submitLabel: string;
  onSubmit: (state: RuleFormState) => Promise<void>;
  onCancel: () => void;
}) {
  const [form, setForm] = useState<RuleFormState>(initial);
  const [submitting, setSubmitting] = useState(false);

  const toggleType = (type: string) =>
    setForm((f) => ({
      ...f,
      selectedTypes: f.selectedTypes.includes(type)
        ? f.selectedTypes.filter((t) => t !== type)
        : [...f.selectedTypes, type],
    }));

  const toggleChannel = (ch: string) =>
    setForm((f) => ({
      ...f,
      channels: f.channels.includes(ch)
        ? f.channels.filter((c) => c !== ch)
        : [...f.channels, ch],
    }));

  const handleSubmit = async () => {
    if (!form.name || (form.selectedTypes.length === 0 && !form.enableFaceRecognition)) return;
    setSubmitting(true);
    try {
      await onSubmit(form);
    } finally {
      setSubmitting(false);
    }
  };

  const isValid = form.name.trim() && (form.selectedTypes.length > 0 || form.enableFaceRecognition);

  return (
    <div className="space-y-4 rounded-lg border bg-card p-4">
      <div>
        <label className="text-sm font-medium">규칙 이름</label>
        <input
          type="text"
          value={form.name}
          onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
          className="mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
          placeholder="예: 화재 알림"
        />
      </div>

      <div>
        <label className="text-sm font-medium">대상 카메라</label>
        <select
          value={form.cameraId}
          onChange={(e) => setForm((f) => ({ ...f, cameraId: e.target.value }))}
          className="mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm"
        >
          <option value="">전체 카메라</option>
          {cameras.map((cam) => (
            <option key={cam.id} value={cam.id}>
              {cam.name} ({cam.ip_address})
            </option>
          ))}
        </select>
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
                form.selectedTypes.includes(dt.value)
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
            onClick={() => setForm((f) => ({ ...f, enableFaceRecognition: !f.enableFaceRecognition }))}
            className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
              form.enableFaceRecognition
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
              onClick={() => setForm((f) => ({ ...f, minSeverity: s }))}
              className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
                form.minSeverity === s
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
                form.channels.includes(ch)
                  ? "bg-primary text-primary-foreground"
                  : "bg-secondary text-secondary-foreground"
              }`}
            >
              {ch}
            </button>
          ))}
        </div>
      </div>

      <div className="flex gap-2">
        <Button onClick={handleSubmit} disabled={submitting || !isValid} size="sm">
          {submitting ? "저장 중..." : submitLabel}
        </Button>
        <Button variant="outline" size="sm" onClick={onCancel}>
          취소
        </Button>
      </div>
    </div>
  );
}

export default function AlertRulesPage() {
  const { rules, isLoading, refresh } = useAlertRules();
  const { cameras } = useCameras();
  const viewMode = useAtomValue(viewModeAtom);
  const [showCreate, setShowCreate] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);

  const getCameraLabel = (cameraId: string | null) => {
    if (!cameraId) return "전체 카메라";
    const cam = cameras.find((c) => c.id === cameraId);
    return cam ? `${cam.name} (${cam.ip_address})` : cameraId.slice(0, 8);
  };

  const handleCreate = async (form: RuleFormState) => {
    await alertApi.createRule({
      name: form.name,
      camera_id: form.cameraId || null,
      danger_types: form.selectedTypes,
      min_severity: form.minSeverity,
      notify_websocket: form.channels.includes("WEBSOCKET"),
      notify_mqtt: form.channels.includes("MQTT"),
      notify_email: form.channels.includes("EMAIL"),
      email_recipients: [],
      enable_face_recognition: form.enableFaceRecognition,
    });
    setShowCreate(false);
    refresh();
  };

  const handleEdit = async (ruleId: string, form: RuleFormState) => {
    await alertApi.updateRule(ruleId, {
      name: form.name,
      camera_id: form.cameraId || null,
      danger_types: form.selectedTypes,
      min_severity: form.minSeverity,
      notify_websocket: form.channels.includes("WEBSOCKET"),
      notify_mqtt: form.channels.includes("MQTT"),
      notify_email: form.channels.includes("EMAIL"),
      email_recipients: [],
      enable_face_recognition: form.enableFaceRecognition,
    });
    setEditingId(null);
    refresh();
  };

  const handleToggleActive = async (ruleId: string, current: boolean) => {
    await alertApi.updateRule(ruleId, { is_active: !current });
    refresh();
  };

  const handleDelete = async (ruleId: string) => {
    await alertApi.deleteRule(ruleId);
    if (editingId === ruleId) setEditingId(null);
    refresh();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold">알림 규칙</h2>
          <p className="mt-1 text-sm text-muted-foreground">{rules.length}개 규칙</p>
        </div>
        <div className="flex items-center gap-2">
          <ViewModeToggle />
          <Button
            onClick={() => {
              setShowCreate(!showCreate);
              setEditingId(null);
            }}
          >
            {showCreate ? "취소" : "규칙 추가"}
          </Button>
        </div>
      </div>

      {showCreate && (
        <RuleForm
          initial={emptyForm()}
          cameras={cameras}
          submitLabel="규칙 생성"
          onSubmit={handleCreate}
          onCancel={() => setShowCreate(false)}
        />
      )}

      <div className={viewMode === "card" ? "space-y-3" : "space-y-1.5"}>
        {isLoading ? (
          <div className="flex h-48 items-center justify-center text-muted-foreground">
            로딩 중...
          </div>
        ) : rules.length === 0 ? (
          <div className="flex h-48 items-center justify-center text-muted-foreground">
            설정된 규칙이 없습니다
          </div>
        ) : (
          rules.map((rule) =>
            editingId === rule.id ? (
              <RuleForm
                key={rule.id}
                initial={ruleToForm(rule)}
                cameras={cameras}
                submitLabel="저장"
                onSubmit={(form) => handleEdit(rule.id, form)}
                onCancel={() => setEditingId(null)}
              />
            ) : viewMode === "card" ? (
              <div key={rule.id} className="flex items-start justify-between rounded-lg border p-4">
                <div className="flex-1">
                  <p className="font-medium">{rule.name}</p>
                  <p className="mt-0.5 text-xs text-muted-foreground">{getCameraLabel(rule.camera_id)}</p>
                  <div className="mt-1.5 flex flex-wrap gap-1">
                    {rule.danger_types.map((dt) => (
                      <span key={dt} className="rounded bg-secondary px-1.5 py-0.5 text-xs">
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
                <div className="ml-3 flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => handleToggleActive(rule.id, rule.is_active)}
                    className={`rounded-full px-2.5 py-0.5 text-xs font-medium transition-colors ${
                      rule.is_active
                        ? "bg-green-100 text-green-700 hover:bg-green-200"
                        : "bg-secondary text-muted-foreground hover:bg-secondary/80"
                    }`}
                  >
                    {rule.is_active ? "활성" : "비활성"}
                  </button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => {
                      setEditingId(rule.id);
                      setShowCreate(false);
                    }}
                  >
                    편집
                  </Button>
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
            ) : (
              <div
                key={rule.id}
                className="flex items-center gap-3 rounded-md border bg-card px-3 py-2 text-sm"
              >
                <span className="w-36 shrink-0 truncate font-medium">{rule.name}</span>
                <span className="w-32 shrink-0 truncate text-xs text-muted-foreground">
                  {getCameraLabel(rule.camera_id)}
                </span>
                <span className="flex-1 truncate text-xs text-muted-foreground">
                  {rule.danger_types
                    .map((dt) => DANGER_TYPES.find((d) => d.value === dt)?.label ?? dt)
                    .join(", ")}
                  {rule.enable_face_recognition &&
                    (rule.danger_types.length ? " · " : "") + "얼굴 검색"}
                </span>
                <span className="w-20 shrink-0 text-right text-[11px] text-muted-foreground">
                  ≥ {rule.min_severity}
                </span>
                <button
                  type="button"
                  onClick={() => handleToggleActive(rule.id, rule.is_active)}
                  className={`w-14 shrink-0 rounded-full px-2 py-0.5 text-center text-[11px] font-medium transition-colors ${
                    rule.is_active
                      ? "bg-green-100 text-green-700 hover:bg-green-200"
                      : "bg-secondary text-muted-foreground hover:bg-secondary/80"
                  }`}
                >
                  {rule.is_active ? "활성" : "비활성"}
                </button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => {
                    setEditingId(rule.id);
                    setShowCreate(false);
                  }}
                >
                  편집
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  className="text-red-500 hover:text-red-700"
                  onClick={() => handleDelete(rule.id)}
                >
                  삭제
                </Button>
              </div>
            ),
          )
        )}
      </div>
    </div>
  );
}
