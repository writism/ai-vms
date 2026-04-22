"use client";

import useSWR from "swr";
import { env } from "@/infrastructure/config/env";

interface UnidentifiedCluster {
  cluster_id: string;
  face_count: number;
  first_seen: string;
  last_seen: string;
  thumbnail_url: string | null;
}

export default function UnidentifiedFacesPage() {
  const { data: clusters, isLoading } = useSWR<UnidentifiedCluster[]>(
    "/api/faces/unidentified/clusters",
    {
      fallbackData: [],
    },
  );

  return (
    <div>
      <div>
        <h2 className="text-2xl font-semibold">미식별 얼굴</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          {clusters?.length ?? 0}개 클러스터
        </p>
      </div>

      <div className="mt-6">
        {isLoading ? (
          <div className="flex h-48 items-center justify-center text-muted-foreground">
            로딩 중...
          </div>
        ) : !clusters || clusters.length === 0 ? (
          <div className="flex h-48 flex-col items-center justify-center gap-2 text-muted-foreground">
            <p>미식별 얼굴 클러스터가 없습니다</p>
            <p className="text-xs">
              카메라에서 인식되었으나 등록된 인물과 매칭되지 않은 얼굴이 여기에 표시됩니다
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
            {clusters.map((cluster) => (
              <div
                key={cluster.cluster_id}
                className="rounded-lg border bg-card p-3"
              >
                <div className="flex aspect-square items-center justify-center rounded-md bg-secondary">
                  {cluster.thumbnail_url ? (
                    <img
                      src={`${env.apiUrl}${cluster.thumbnail_url}`}
                      alt="unidentified"
                      className="h-full w-full rounded-md object-cover"
                    />
                  ) : (
                    <span className="text-3xl text-muted-foreground">?</span>
                  )}
                </div>
                <div className="mt-2">
                  <p className="text-sm font-medium">
                    {cluster.face_count}회 감지
                  </p>
                  <p className="text-xs text-muted-foreground">
                    최초: {new Date(cluster.first_seen).toLocaleDateString("ko-KR")}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    최근: {new Date(cluster.last_seen).toLocaleDateString("ko-KR")}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
