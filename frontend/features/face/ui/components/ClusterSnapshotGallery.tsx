"use client";

import { useEffect, useState } from "react";
import { env } from "@/infrastructure/config/env";
import { faceApi, type ClusterSnapshot, type FaceSuggestion } from "../../infrastructure/api/faceApi";
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
  const [loading, setLoading] = useState(true);
  const [enlarged, setEnlarged] = useState<string | null>(null);
  const [ignoring, setIgnoring] = useState(false);

  useEffect(() => {
    faceApi
      .getClusterSnapshots(suggestion.cluster_id)
      .then(setSnapshots)
      .finally(() => setLoading(false));
  }, [suggestion.cluster_id]);

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

  const lastSeen = formatTimestamp(suggestion.last_seen);

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
                    return (
                      <button
                        key={snap.log_id}
                        onClick={() => setEnlarged(url)}
                        className="group relative rounded-md border border-border overflow-hidden aspect-square hover:border-primary focus:outline-none focus:ring-2 focus:ring-primary"
                        title={`신뢰도 ${Math.round(snap.confidence * 100)}% · ${time}`}
                      >
                        <img
                          src={url}
                          alt="스냅샷"
                          className="h-full w-full object-cover group-hover:opacity-90 transition-opacity"
                        />
                        <span className="absolute bottom-0 left-0 right-0 bg-black/60 px-1 py-0.5 text-center text-[10px] text-white">
                          {Math.round(snap.confidence * 100)}%
                        </span>
                      </button>
                    );
                  })}
                </div>
              )}
            </div>

            <div className="shrink-0 flex items-center justify-between border-t border-border px-6 py-4">
              <p className="text-xs text-muted-foreground">
                {snapshots.length}개 이미지 (클릭하면 확대)
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
