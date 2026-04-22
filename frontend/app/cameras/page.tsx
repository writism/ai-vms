"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { useCameras } from "@/features/camera/application/hooks/useCameras";
import { CameraGrid } from "@/features/camera/ui/components/CameraGrid";
import { DiscoveryDialog } from "@/features/camera/ui/components/DiscoveryDialog";

export default function CamerasPage() {
  const { cameras, isLoading, refresh } = useCameras();
  const [discoveryOpen, setDiscoveryOpen] = useState(false);

  return (
    <div>
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold">카메라 관리</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            {cameras.length}대 등록됨
          </p>
        </div>
        <Button onClick={() => setDiscoveryOpen(true)}>카메라 검색</Button>
      </div>

      <div className="mt-6">
        {isLoading ? (
          <div className="flex h-48 items-center justify-center text-muted-foreground">
            로딩 중...
          </div>
        ) : (
          <CameraGrid cameras={cameras} />
        )}
      </div>

      <DiscoveryDialog
        open={discoveryOpen}
        onClose={() => setDiscoveryOpen(false)}
        onRegistered={() => refresh()}
      />
    </div>
  );
}
