"use client";

import { use } from "react";
import useSWR from "swr";
import Link from "next/link";
import type { Camera } from "@/features/camera/domain/model/camera";
import { VideoPlayer } from "@/features/stream/ui/components/VideoPlayer";

const statusColors: Record<string, string> = {
  ONLINE: "bg-green-500",
  OFFLINE: "bg-gray-400",
  ERROR: "bg-red-500",
};

const statusLabels: Record<string, string> = {
  ONLINE: "온라인",
  OFFLINE: "오프라인",
  ERROR: "오류",
};

export default function CameraDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const { data: camera, isLoading } = useSWR<Camera>(`/api/cameras/${id}`);

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

      <div className="flex items-center gap-3">
        <div
          className={`h-3 w-3 rounded-full ${statusColors[camera.status]}`}
        />
        <h2 className="text-2xl font-semibold">{camera.name}</h2>
        <span className="text-sm text-muted-foreground">
          {statusLabels[camera.status]}
        </span>
      </div>

      <div className="aspect-video w-full overflow-hidden rounded-lg border bg-black">
        {camera.rtsp_url ? (
          <VideoPlayer streamName={camera.id} />
        ) : (
          <div className="flex h-full items-center justify-center text-white/50">
            RTSP URL 미설정
          </div>
        )}
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div className="rounded-lg border bg-card p-4">
          <h3 className="mb-3 font-semibold">카메라 정보</h3>
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
        </div>

        <div className="rounded-lg border bg-card p-4">
          <h3 className="mb-3 font-semibold">AI 분석 상태</h3>
          <div className="space-y-3 text-sm">
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">얼굴 인식</span>
              <span className="rounded bg-secondary px-2 py-0.5 text-xs">
                {camera.status === "ONLINE" ? "활성" : "비활성"}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">위험 감지</span>
              <span className="rounded bg-secondary px-2 py-0.5 text-xs">
                {camera.status === "ONLINE" ? "활성" : "비활성"}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">모션 게이팅</span>
              <span className="rounded bg-secondary px-2 py-0.5 text-xs">
                활성
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
