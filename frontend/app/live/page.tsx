"use client";

import { useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { useCameras } from "@/features/camera/application/hooks/useCameras";
import { streamApi } from "@/features/stream/infrastructure/api/streamApi";
import { MultiView } from "@/features/stream/ui/components/MultiView";

type GridLayout = 1 | 4 | 9 | 16;

export default function LiveViewPage() {
  const { cameras } = useCameras();
  const [layout, setLayout] = useState<GridLayout>(4);
  const registeredRef = useRef(false);

  useEffect(() => {
    if (cameras.length === 0 || registeredRef.current) return;
    registeredRef.current = true;
    Promise.allSettled(
      cameras
        .filter((c) => c.rtsp_url)
        .map((c) => streamApi.register(c.id, c.rtsp_url!)),
    );
  }, [cameras]);

  const streams = cameras.map((c) => ({ name: c.id, rtspUrl: c.rtsp_url }));

  return (
    <div>
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold">라이브뷰</h2>
        <div className="flex gap-1">
          {([1, 4, 9, 16] as GridLayout[]).map((l) => (
            <Button
              key={l}
              size="sm"
              variant={layout === l ? "default" : "outline"}
              onClick={() => setLayout(l)}
            >
              {l === 1 ? "1x1" : l === 4 ? "2x2" : l === 9 ? "3x3" : "4x4"}
            </Button>
          ))}
        </div>
      </div>

      <div className="mt-4">
        <MultiView streams={streams} layout={layout} />
      </div>
    </div>
  );
}
