"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { env } from "@/infrastructure/config/env";
import { faceApi, type FaceSuggestion } from "../../infrastructure/api/faceApi";
import { formatTimestamp } from "../lib/format-time";
import { ClusterSnapshotGallery } from "./ClusterSnapshotGallery";

export function FaceSuggestionCard({
  suggestion,
  onRegister,
  onResolved,
}: {
  suggestion: FaceSuggestion;
  onRegister: (s: FaceSuggestion) => void;
  onResolved: () => void;
}) {
  const [galleryOpen, setGalleryOpen] = useState(false);
  const [ignoring, setIgnoring] = useState(false);
  const photoUrl = suggestion.image_url
    ? `${env.apiUrl}${suggestion.image_url}`
    : null;
  const lastSeen = formatTimestamp(suggestion.last_seen);
  const camera = suggestion.last_camera_id
    ? suggestion.last_camera_id.slice(0, 8)
    : "-";

  const handleIgnore = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm("이 후보를 무시하시겠습니까? (24시간 동안 재추천되지 않습니다)")) return;
    setIgnoring(true);
    try {
      await faceApi.ignoreSuggestion(suggestion.cluster_id);
      onResolved();
    } finally {
      setIgnoring(false);
    }
  };

  const handleRegister = (e: React.MouseEvent) => {
    e.stopPropagation();
    setGalleryOpen(true);
  };

  return (
    <>
      <div
        onClick={() => setGalleryOpen(true)}
        className="cursor-pointer rounded-lg border border-amber-300 bg-amber-50 p-3 transition-colors hover:bg-amber-100/70 dark:border-amber-800 dark:bg-amber-950/40 dark:hover:bg-amber-900/40"
      >
        <div className="flex items-center gap-3">
          {photoUrl ? (
            <img
              src={photoUrl}
              alt="얼굴 후보"
              className="h-14 w-14 shrink-0 rounded-full border border-border object-cover"
            />
          ) : (
            <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full border border-amber-400 bg-amber-100 text-xs text-amber-800 dark:bg-amber-900/30 dark:text-amber-300">
              ?
            </div>
          )}
          <div className="flex-1 text-sm">
            <p className="font-semibold text-amber-900 dark:text-amber-200">
              24시간 내 {suggestion.count_window}회 검출
            </p>
            <p className="mt-0.5 text-xs text-amber-800 dark:text-amber-300">
              평균 신뢰도 {Math.round(suggestion.avg_confidence * 100)}% · 최근 {lastSeen}
            </p>
            <p className="mt-0.5 font-mono text-[10px] text-muted-foreground">
              cam: {camera}
            </p>
          </div>
        </div>
        <div className="mt-3 flex justify-end gap-2">
          <Button size="sm" variant="outline" onClick={handleIgnore} disabled={ignoring}>
            {ignoring ? "처리 중..." : "무시"}
          </Button>
          <Button size="sm" onClick={handleRegister}>
            등록
          </Button>
        </div>
      </div>

      {galleryOpen && (
        <ClusterSnapshotGallery
          suggestion={suggestion}
          onClose={() => setGalleryOpen(false)}
          onRegister={() => {
            setGalleryOpen(false);
            onRegister(suggestion);
          }}
          onIgnore={onResolved}
        />
      )}
    </>
  );
}
