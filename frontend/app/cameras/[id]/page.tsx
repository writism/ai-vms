"use client";

import { use, useState } from "react";
import { useRouter } from "next/navigation";
import useSWR, { useSWRConfig } from "swr";
import Link from "next/link";
import type { Camera } from "@/features/camera/domain/model/camera";
import { VideoPlayer } from "@/features/stream/ui/components/VideoPlayer";
import { cameraApi } from "@/features/camera/infrastructure/api/cameraApi";
import { Button } from "@/components/ui/button";
import { cameraStatusColors, cameraStatusLabels } from "@/lib/constants/labels";
import { env } from "@/infrastructure/config/env";

interface HealthResponse {
  services: {
    insightface: boolean;
    yolo: boolean;
  };
}

export default function CameraDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const { data: camera, isLoading, mutate } = useSWR<Camera>(`/api/cameras/${id}`, { refreshInterval: 10000 });
  const { data: health } = useSWR<HealthResponse>(`${env.apiUrl}/health`, (url: string) => fetch(url).then((r) => r.json()));
  const [editing, setEditing] = useState(false);
  const [editName, setEditName] = useState("");
  const [editRtspUrl, setEditRtspUrl] = useState("");
  const [saving, setSaving] = useState(false);

  const router = useRouter();
  const { mutate: globalMutate } = useSWRConfig();
  const [onvifUser, setOnvifUser] = useState("admin");
  const [onvifPass, setOnvifPass] = useState("");
  const [showPass, setShowPass] = useState(false);
  const [fetching, setFetching] = useState(false);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  if (isLoading) {
    return (
      <div className="flex h-48 items-center justify-center text-muted-foreground">
        로딩 중...
      </div>
    );
  }

  if (!camera) {
    return (
      <div className="flex h-48 items-center justify-center text-muted-foreground">
        카메라를 찾을 수 없습니다
      </div>
    );
  }

  const startEdit = () => {
    setEditName(camera.name);
    setEditRtspUrl(camera.rtsp_url ?? "");
    setEditing(true);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await cameraApi.update(id, {
        name: editName || undefined,
        rtsp_url: editRtspUrl || undefined,
      });
      await mutate();
      setEditing(false);
    } finally {
      setSaving(false);
    }
  };

  const handleFetchRtsp = async () => {
    if (!onvifUser || !onvifPass) return;
    setFetching(true);
    setFetchError(null);
    try {
      await cameraApi.fetchRtspUrl(id, {
        username: onvifUser,
        password: onvifPass,
      });
      await mutate();
      setOnvifUser("");
      setOnvifPass("");
    } catch (e) {
      setFetchError(
        e instanceof Error ? e.message : "RTSP URL 조회에 실패했습니다",
      );
    } finally {
      setFetching(false);
    }
  };

  const handleDelete = async () => {
    setDeleting(true);
    setDeleteError(null);
    try {
      await cameraApi.delete(id);
      await globalMutate("/api/cameras");
      router.push("/cameras");
    } catch (e) {
      const msg = e instanceof Error ? e.message : "삭제에 실패했습니다";
      const match = msg.match(/"message"\s*:\s*"([^"]+)"/);
      setDeleteError(match ? match[1] : msg);
      setShowDeleteConfirm(false);
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link
          href="/cameras"
          className="text-sm text-muted-foreground hover:text-foreground"
        >
          ← 카메라 목록
        </Link>
      </div>

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div
            className={`h-3 w-3 rounded-full ${cameraStatusColors[camera.status]}`}
          />
          <h2 className="text-2xl font-semibold">{camera.name}</h2>
          <span className="text-sm text-muted-foreground">
            {cameraStatusLabels[camera.status]}
          </span>
        </div>
        <Button
          variant="outline"
          size="sm"
          className="text-red-600 border-red-300 hover:bg-red-50 hover:text-red-700 dark:border-red-800 dark:hover:bg-red-950"
          onClick={() => { setDeleteError(null); setShowDeleteConfirm(true); }}
        >
          삭제
        </Button>
      </div>

      {deleteError && (
        <div className="rounded-lg border border-red-300 bg-red-50 p-3 text-sm text-red-700 dark:border-red-800 dark:bg-red-950 dark:text-red-400">
          {deleteError}
        </div>
      )}

      {showDeleteConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="mx-4 w-full max-w-sm rounded-lg border bg-card p-6 shadow-lg">
            <h3 className="text-lg font-semibold">카메라 삭제</h3>
            <p className="mt-2 text-sm text-muted-foreground">
              <strong>{camera.name}</strong> 카메라를 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.
            </p>
            <div className="mt-4 flex justify-end gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowDeleteConfirm(false)}
                disabled={deleting}
              >
                취소
              </Button>
              <Button
                size="sm"
                className="bg-red-600 text-white hover:bg-red-700"
                onClick={handleDelete}
                disabled={deleting}
              >
                {deleting ? "삭제 중..." : "삭제"}
              </Button>
            </div>
          </div>
        </div>
      )}

      <div className="aspect-video w-full overflow-hidden rounded-lg border bg-black">
        {camera.rtsp_url ? (
          <VideoPlayer streamName={camera.id} rtspUrl={camera.rtsp_url} />
        ) : (
          <div className="flex h-full items-center justify-center text-white/50">
            RTSP URL 미설정
          </div>
        )}
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div className="rounded-lg border bg-card p-4">
          <div className="mb-3 flex items-center justify-between">
            <h3 className="font-semibold">카메라 정보</h3>
            {!editing && (
              <Button size="sm" variant="outline" onClick={startEdit}>
                편집
              </Button>
            )}
          </div>

          {editing ? (
            <div className="space-y-3">
              <div>
                <label className="text-xs text-muted-foreground">이름</label>
                <input
                  type="text"
                  value={editName}
                  onChange={(e) => setEditName(e.target.value)}
                  className="mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm"
                />
              </div>
              <div>
                <label className="text-xs text-muted-foreground">
                  RTSP URL
                </label>
                <input
                  type="text"
                  value={editRtspUrl}
                  onChange={(e) => setEditRtspUrl(e.target.value)}
                  placeholder="rtsp://..."
                  className="mt-1 w-full rounded-md border bg-background px-3 py-2 font-mono text-xs"
                />
              </div>
              <div className="flex gap-2">
                <Button size="sm" onClick={handleSave} disabled={saving}>
                  {saving ? "저장 중..." : "저장"}
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => setEditing(false)}
                >
                  취소
                </Button>
              </div>
            </div>
          ) : (
            <dl className="space-y-2 text-sm">
              <div className="flex justify-between">
                <dt className="text-muted-foreground">IP 주소</dt>
                <dd className="font-mono">{camera.ip_address}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-muted-foreground">ONVIF 포트</dt>
                <dd className="font-mono">{camera.onvif_port}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-muted-foreground">RTSP URL</dt>
                <dd className="max-w-[250px] truncate font-mono text-xs">
                  {camera.rtsp_url ?? "-"}
                </dd>
              </div>
              {camera.manufacturer && (
                <div className="flex justify-between">
                  <dt className="text-muted-foreground">제조사</dt>
                  <dd>{camera.manufacturer}</dd>
                </div>
              )}
              {camera.model && (
                <div className="flex justify-between">
                  <dt className="text-muted-foreground">모델</dt>
                  <dd>{camera.model}</dd>
                </div>
              )}
              <div className="flex justify-between">
                <dt className="text-muted-foreground">등록일</dt>
                <dd>
                  {new Date(camera.created_at).toLocaleDateString("ko-KR")}
                </dd>
              </div>
            </dl>
          )}
        </div>

        <div className="space-y-4">
          <div className="rounded-lg border bg-card p-4">
            <h3 className="mb-3 font-semibold">ONVIF RTSP 자동 설정</h3>
            <div className="space-y-2">
              <input
                type="text"
                value={onvifUser}
                onChange={(e) => setOnvifUser(e.target.value)}
                placeholder="카메라 사용자명"
                className="w-full rounded-md border bg-background px-3 py-2 text-sm"
              />
              <div className="relative">
                <input
                  type={showPass ? "text" : "password"}
                  value={onvifPass}
                  onChange={(e) => setOnvifPass(e.target.value)}
                  placeholder="카메라 비밀번호"
                  className="w-full rounded-md border bg-background px-3 py-2 pr-9 text-sm"
                />
                <button
                  type="button"
                  onClick={() => setShowPass(!showPass)}
                  className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                  tabIndex={-1}
                >
                  {showPass ? (
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/>
                      <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/>
                      <line x1="1" y1="1" x2="23" y2="23"/>
                    </svg>
                  ) : (
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                      <circle cx="12" cy="12" r="3"/>
                    </svg>
                  )}
                </button>
              </div>
              <Button
                size="sm"
                className="w-full"
                onClick={handleFetchRtsp}
                disabled={fetching || !onvifUser || !onvifPass}
              >
                {fetching ? "조회 중..." : "RTSP URL 자동 조회"}
              </Button>
              {fetchError && (
                <p className="text-xs text-red-500">{fetchError}</p>
              )}
              <p className="text-xs text-muted-foreground">
                ONVIF를 통해 카메라에서 RTSP URL을 자동으로 가져옵니다
              </p>
            </div>
          </div>

          <div className="rounded-lg border bg-card p-4">
            <h3 className="mb-3 font-semibold">AI 분석 상태</h3>
            <div className="space-y-3 text-sm">
              {health ? (
                <>
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">얼굴 인식</span>
                    <span className={`rounded px-2 py-0.5 text-xs ${health.services.insightface ? "bg-green-100 text-green-700" : "bg-secondary text-muted-foreground"}`}>
                      {health.services.insightface ? "활성" : "비활성"}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">위험 감지</span>
                    <span className={`rounded px-2 py-0.5 text-xs ${health.services.yolo ? "bg-green-100 text-green-700" : "bg-secondary text-muted-foreground"}`}>
                      {health.services.yolo ? "활성" : "비활성"}
                    </span>
                  </div>
                </>
              ) : (
                <p className="text-muted-foreground">확인 중...</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
