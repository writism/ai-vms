"use client";

import { useEffect, useState, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { env } from "@/infrastructure/config/env";
import { cn } from "@/lib/utils";
import { formatTimestamp } from "../lib/format-time";
import { faceApi, type SimilarIdentity } from "../../infrastructure/api/faceApi";
import type { Identity } from "../../domain/model/face";

export interface RecognitionDetailData {
  logId?: string | null;
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

function imgSrc(url: string | null | undefined): string | null {
  if (!url) return null;
  return url.startsWith("http") ? url : `${env.apiUrl}${url}`;
}

export function RecognitionDetailDialog({
  open,
  onClose,
  data,
  onAssigned,
}: {
  open: boolean;
  onClose: () => void;
  data: RecognitionDetailData | null;
  onAssigned?: () => void;
}) {
  const [matches, setMatches] = useState<SimilarIdentity[]>([]);
  const [loadingMatches, setLoadingMatches] = useState(false);
  const [assigning, setAssigning] = useState<string | null>(null);
  const [assigned, setAssigned] = useState<string | null>(null);

  const [showManual, setShowManual] = useState(false);
  const [identities, setIdentities] = useState<Identity[]>([]);
  const [search, setSearch] = useState("");
  const [loadingIdents, setLoadingIdents] = useState(false);

  const isUnregistered = data?.isRegistered === false;

  const fetchMatches = useCallback(async (logId: string) => {
    setLoadingMatches(true);
    try {
      const res = await faceApi.matchRecognitionLog(logId, 5);
      setMatches(res);
    } catch {
      setMatches([]);
    } finally {
      setLoadingMatches(false);
    }
  }, []);

  const fetchIdentities = useCallback(async () => {
    setLoadingIdents(true);
    try {
      const res = await faceApi.listIdentities();
      setIdentities(res);
    } catch {
      setIdentities([]);
    } finally {
      setLoadingIdents(false);
    }
  }, []);

  useEffect(() => {
    if (!open) {
      setMatches([]);
      setAssigned(null);
      setAssigning(null);
      setShowManual(false);
      setSearch("");
      return;
    }
    if (isUnregistered && data?.logId) {
      fetchMatches(data.logId);
    }
  }, [open, data?.logId, isUnregistered, fetchMatches]);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  useEffect(() => {
    if (showManual && identities.length === 0) {
      fetchIdentities();
    }
  }, [showManual, identities.length, fetchIdentities]);

  const handleAssign = useCallback(
    async (identityId: string) => {
      if (!data?.logId) return;
      setAssigning(identityId);
      try {
        const res = await faceApi.assignRecognitionLog(data.logId, identityId);
        setAssigned(res.identity_name);
        onAssigned?.();
      } catch {
        alert("등록 중 오류가 발생했습니다.");
      } finally {
        setAssigning(null);
      }
    },
    [data?.logId, onAssigned],
  );

  if (!open || !data) return null;

  const fullSrc = imgSrc(data.imageUrl);
  const occurred = formatTimestamp(data.occurredAt);
  const camera = data.cameraId ? data.cameraId.slice(0, 8) : "-";

  const filtered = identities.filter((id) => {
    const q = search.toLowerCase();
    return (
      id.name.toLowerCase().includes(q) ||
      (id.department ?? "").toLowerCase().includes(q) ||
      (id.employee_id ?? "").toLowerCase().includes(q)
    );
  });

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="w-full max-w-lg max-h-[90vh] overflow-y-auto rounded-xl border border-border bg-card p-5 shadow-2xl"
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
              className="block max-h-[40vh] w-full object-contain"
            />
          ) : (
            <div className="flex h-48 items-center justify-center text-sm text-muted-foreground">
              스냅샷 없음
            </div>
          )}
        </div>

        <dl className="mt-4 space-y-1.5 text-sm">
          <div className="flex justify-between">
            <dt className="text-muted-foreground">일치도</dt>
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

        {isUnregistered && (
          <div className="mt-5 border-t border-border pt-4">
            {assigned ? (
              <div className="rounded-lg bg-green-500/10 border border-green-500/30 px-4 py-3 text-sm text-green-600">
                ✓ <span className="font-semibold">{assigned}</span>으로 등록되었습니다.
              </div>
            ) : (
              <>
                <p className="mb-3 text-sm font-medium">유사 인물 추천</p>

                {loadingMatches ? (
                  <div className="py-4 text-center text-xs text-muted-foreground">
                    유사 인물 검색 중...
                  </div>
                ) : matches.length === 0 ? (
                  <div className="py-3 text-center text-xs text-muted-foreground">
                    유사한 등록 인물을 찾지 못했습니다.
                  </div>
                ) : (
                  <div className="space-y-2">
                    {matches.map((m) => {
                      const face = imgSrc(m.face_image_url);
                      return (
                        <div
                          key={m.identity_id}
                          className="flex items-center gap-3 rounded-lg border border-border bg-secondary/30 px-3 py-2"
                        >
                          <div className="h-12 w-12 shrink-0 overflow-hidden rounded-full border border-border bg-muted">
                            {face ? (
                              <img
                                src={face}
                                alt={m.name}
                                className="h-full w-full object-cover"
                              />
                            ) : (
                              <div className="flex h-full w-full items-center justify-center text-lg text-muted-foreground">
                                ?
                              </div>
                            )}
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="font-semibold text-sm truncate">{m.name}</p>
                            {m.position && (
                              <p className="text-xs text-muted-foreground">{m.position}</p>
                            )}
                            {m.department && (
                              <p className="text-xs text-muted-foreground">{m.department}</p>
                            )}
                          </div>
                          <div className="flex shrink-0 flex-col items-end gap-1.5">
                            <span
                              className={cn(
                                "font-mono text-sm font-bold",
                                m.score >= 80
                                  ? "text-green-500"
                                  : m.score >= 60
                                    ? "text-yellow-500"
                                    : "text-red-400",
                              )}
                            >
                              {m.score.toFixed(1)}%
                            </span>
                            <Button
                              size="sm"
                              className="h-7 text-xs"
                              disabled={assigning !== null}
                              onClick={() => handleAssign(m.identity_id)}
                            >
                              {assigning === m.identity_id ? "등록 중..." : "이 사람으로 등록"}
                            </Button>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}

                <button
                  type="button"
                  className="mt-3 text-xs text-muted-foreground underline underline-offset-2 hover:text-foreground"
                  onClick={() => setShowManual((v) => !v)}
                >
                  {showManual ? "▲ 직접 선택 닫기" : "▼ 목록에서 직접 선택"}
                </button>

                {showManual && (
                  <div className="mt-2 space-y-2">
                    <input
                      type="text"
                      placeholder="이름, 부서, 사번 검색..."
                      value={search}
                      onChange={(e) => setSearch(e.target.value)}
                      className="w-full rounded-md border border-border bg-background px-3 py-1.5 text-sm outline-none focus:border-ring"
                    />
                    {loadingIdents ? (
                      <div className="py-2 text-center text-xs text-muted-foreground">
                        로딩 중...
                      </div>
                    ) : (
                      <div className="max-h-48 overflow-y-auto space-y-1">
                        {filtered.length === 0 ? (
                          <div className="py-2 text-center text-xs text-muted-foreground">
                            검색 결과 없음
                          </div>
                        ) : (
                          filtered.map((id) => (
                            <div
                              key={id.id}
                              className="flex items-center justify-between rounded border border-border px-3 py-1.5"
                            >
                              <div>
                                <span className="text-sm font-medium">{id.name}</span>
                                {id.position && (
                                  <span className="ml-1.5 text-xs text-muted-foreground">
                                    {id.position}
                                  </span>
                                )}
                                {id.department && (
                                  <span className="ml-1.5 text-xs text-muted-foreground">
                                    · {id.department}
                                  </span>
                                )}
                              </div>
                              <Button
                                size="sm"
                                variant="outline"
                                className="h-6 text-xs"
                                disabled={assigning !== null}
                                onClick={() => handleAssign(id.id)}
                              >
                                {assigning === id.id ? "..." : "등록"}
                              </Button>
                            </div>
                          ))
                        )}
                      </div>
                    )}
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
