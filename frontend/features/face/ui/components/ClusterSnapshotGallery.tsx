"use client";

import { useEffect, useState } from "react";
import { env } from "@/infrastructure/config/env";
import { faceApi, type ClusterSnapshot, type FaceSuggestion, type OutlierSnapshot } from "../../infrastructure/api/faceApi";
import { formatTimestamp, formatShort } from "../lib/format-time";
import { Button } from "@/components/ui/button";

export function ClusterSnapshotGallery({
  suggestion,
  onClose,
  onRegister,
  onIgnore,
}: {
  suggestion: FaceSuggestion;
  onClose: () => void;
  onRegister: () => void;
  onIgnore: () => void;
}) {
  const [snapshots, setSnapshots] = useState<ClusterSnapshot[]>([]);
  const [outliers, setOutliers] = useState<Record<string, OutlierSnapshot>>({});
  const [loading, setLoading] = useState(true);
  const [enlarged, setEnlarged] = useState<string | null>(null);
  const [ignoring, setIgnoring] = useState(false);
  const [deletingIds, setDeletingIds] = useState<Set<string>>(new Set());

  const load = () => {
    setLoading(true);
    Promise.all([
      faceApi.getClusterSnapshots(suggestion.cluster_id),
      faceApi.getClusterOutliers(suggestion.cluster_id),
    ])
      .then(([snaps, outs]) => {
        setSnapshots(snaps);
        const map: Record<string, OutlierSnapshot> = {};
        for (const o of outs) map[o.log_id] = o;
        setOutliers(map);
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, [suggestion.cluster_id]);

  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        if (enlarged) setEnlarged(null);
        else onClose();
      }
    };
    document.addEventListener("keydown", handleKey);
    return () => document.removeEventListener("keydown", handleKey);
  }, [enlarged, onClose]);

  const handleIgnore = async () => {
    if (!confirm("이 후보를 무시하시겠습니까? (24시간 동안 재추천되지 않습니다)")) return;
    setIgnoring(true);
    try {
      await faceApi.ignoreSuggestion(suggestion.cluster_id);
      onIgnore();
      onClose();
    } finally {
      setIgnoring(false);
    }
  };

  const handleDeleteSnapshot = async (e: React.MouseEvent, logId: string) => {
    e.stopPropagation();
    if (!confirm("이 스냅샷을 삭제하시겠습니까?")) return;
    setDeletingIds((prev) => new Set(prev).add(logId));
    try {
      await faceApi.deleteClusterSnapshot(suggestion.cluster_id, logId);
      setSnapshots((prev) => prev.filter((s) => s.log_id !== logId));
      setOutliers((prev) => {
        const next = { ...prev };
        delete next[logId];
        return next;
      });
    } finally {
      setDeletingIds((prev) => {
        const next = new Set(prev);
        next.delete(logId);
        return next;
      });
    }
  };

  const lastSeen = formatTimestamp(suggestion.last_seen);
  const outlierCount = snapshots.filter((s) => outliers[s.log_id]?.is_outlier).length;

  return (
    <>
      <div
        className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
        onClick={enlarged ? () => setEnlarged(null) : onClose}
      >
        {enlarged ? (
          <img
            src={enlarged}
            alt="확대 보기"
            className="max-h-[90vh] max-w-[90vw] rounded-lg object-contain shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          />
        ) : (
          <div
            className="flex max-h-[90vh] w-full max-w-2xl flex-col rounded-xl border border-border bg-card shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="shrink-0 flex items-center justify-between border-b border-border px-6 py-4">
              <div>
                <h2 className="text-base font-semibold">캡처된 얼굴 이미지</h2>
                <p className="mt-0.5 text-xs text-muted-foreground">
                  24시간 내 {suggestion.count_window}회 검출 · 최근 {lastSeen}
                </p>
                {outlierCount > 0 && (
                  <p className="mt-0.5 text-xs text-orange-600">
                    이상치 {outlierCount}개 감지 — 다른 인물이 섞였을 수 있습니다
                  </p>
                )}
              </div>
              <button
                onClick={onClose}
                className="text-muted-foreground hover:text-foreground text-lg leading-none"
              >
                ✕
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-4">
              {loading ? (
                <div className="flex h-32 items-center justify-center text-sm text-muted-foreground">
                  로딩 중...
                </div>
              ) : snapshots.length === 0 ? (
                <div className="flex h-32 items-center justify-center text-sm text-muted-foreground">
                  캡처된 이미지가 없습니다
                </div>
              ) : (
                <div className="grid grid-cols-4 gap-2 sm:grid-cols-5">
                  {snapshots.map((snap) => {
                    const url = `${env.apiUrl}${snap.image_url}`;
                    const time = formatShort(snap.created_at);
                    const outlier = outliers[snap.log_id];
                    const isOutlier = outlier?.is_outlier ?? false;
                    const simPct = outlier ? Math.round(outlier.similarity_to_mean * 100) : null;
                    const isDeleting = deletingIds.has(snap.log_id);
                    return (
                      <div
                        key={snap.log_id}
                        className={`group relative rounded-md border overflow-hidden aspect-square ${
                          isOutlier
                            ? "border-orange-400 ring-1 ring-orange-400"
                            : "border-border"
                        }`}
                      >
                        <button
                          onClick={() => setEnlarged(url)}
                          className="block h-full w-full focus:outline-none"
                          title={`신뢰도 ${Math.round(snap.confidence * 100)}%${simPct !== null ? ` · 유사도 ${simPct}%` : ""} · ${time}`}
                          disabled={isDeleting}
                        >
                          <img
                            src={url}
                            alt="스냅샷"
                            className="h-full w-full object-cover group-hover:opacity-80 transition-opacity"
                          />
                        </button>

                        {isOutlier && (
                          <div
                            className="absolute top-0.5 left-0.5 rounded bg-orange-500/90 px-1 text-[9px] font-bold text-white leading-4"
                            title={`클러스터 평균과 유사도 ${simPct}% — 이상치`}
                          >
                            이상
                          </div>
                        )}

                        <span className="absolute bottom-0 left-0 right-0 bg-black/60 px-1 py-0.5 text-center text-[10px] text-white">
                          {Math.round(snap.confidence * 100)}%
                        </span>

                        <button
                          onClick={(e) => handleDeleteSnapshot(e, snap.log_id)}
                          disabled={isDeleting}
                          className="absolute top-0.5 right-0.5 hidden group-hover:flex h-5 w-5 items-center justify-center rounded bg-black/70 text-[10px] text-white hover:bg-red-600 disabled:opacity-50"
                          title="삭제"
                        >
                          ✕
                        </button>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            <div className="shrink-0 flex items-center justify-between border-t border-border px-6 py-4">
              <p className="text-xs text-muted-foreground">
                {snapshots.length}개 이미지 · 이미지 위에서 ✕로 삭제 가능
              </p>
              <div className="flex gap-2">
                <Button size="sm" variant="outline" onClick={handleIgnore} disabled={ignoring}>
                  {ignoring ? "처리 중..." : "무시"}
                </Button>
                <Button size="sm" onClick={onRegister}>
                  등록
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  );
}
