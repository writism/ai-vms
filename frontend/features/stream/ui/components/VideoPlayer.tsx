"use client";

import { useEffect } from "react";
import { useWebRTC } from "../../application/hooks/useWebRTC";
import { cn } from "@/lib/utils";

export function VideoPlayer({
  streamName,
  className,
  autoPlay = true,
}: {
  streamName: string;
  className?: string;
  autoPlay?: boolean;
}) {
  const { state, videoRef, connect, disconnect } = useWebRTC(streamName);

  useEffect(() => {
    if (autoPlay) {
      connect();
    }
    return () => {
      disconnect();
    };
  }, [streamName, autoPlay, connect, disconnect]);

  return (
    <div className={cn("relative overflow-hidden rounded-lg bg-black", className)}>
      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted
        className="h-full w-full object-contain"
      />
      {state === "connecting" && (
        <div className="absolute inset-0 flex items-center justify-center text-white/70">
          연결 중...
        </div>
      )}
      {state === "failed" && (
        <div className="absolute inset-0 flex flex-col items-center justify-center gap-2 text-white/70">
          <span>연결 실패</span>
          <button
            onClick={connect}
            className="rounded bg-white/20 px-3 py-1 text-sm hover:bg-white/30"
          >
            재시도
          </button>
        </div>
      )}
      {state === "idle" && (
        <div className="absolute inset-0 flex items-center justify-center text-white/40">
          스트림 대기
        </div>
      )}
    </div>
  );
}
