"use client";

import { useState } from "react";
import { useAtomValue } from "jotai";
import { Button } from "@/components/ui/button";
import { useCameras } from "@/features/camera/application/hooks/useCameras";
import { CameraGrid } from "@/features/camera/ui/components/CameraGrid";
import { CameraListRow } from "@/features/camera/ui/components/CameraListRow";
import { DiscoveryDialog } from "@/features/camera/ui/components/DiscoveryDialog";
import { ViewModeToggle } from "@/ui/components/ViewModeToggle";
import { viewModeAtom } from "@/features/preferences/application/atoms/viewModeAtom";

export default function CamerasPage() {
  const { cameras, isLoading, refresh } = useCameras();
  const viewMode = useAtomValue(viewModeAtom);
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
        <div className="flex items-center gap-2">
          <ViewModeToggle />
          <Button onClick={() => setDiscoveryOpen(true)}>카메라 검색</Button>
        </div>
      </div>

      <div className="mt-6">
        {isLoading ? (
          <div className="flex h-48 items-center justify-center text-muted-foreground">
            로딩 중...
          </div>
        ) : viewMode === "card" ? (
          <CameraGrid cameras={cameras} />
        ) : (
          <div className="space-y-1.5">
            {cameras.map((c) => (
              <CameraListRow key={c.id} camera={c} />
            ))}
          </div>
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
