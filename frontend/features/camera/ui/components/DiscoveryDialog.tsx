"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { useCameraDiscovery } from "../../application/hooks/useCameraDiscovery";
import { cameraApi } from "../../infrastructure/api/cameraApi";
import type { DiscoveredCamera } from "../../domain/model/camera";

export function DiscoveryDialog({
  open,
  onClose,
  onRegistered,
}: {
  open: boolean;
  onClose: () => void;
  onRegistered: () => void;
}) {
  const { state, discover, reset } = useCameraDiscovery();
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [registering, setRegistering] = useState(false);

  if (!open) return null;

  const handleDiscover = () => {
    setSelected(new Set());
    discover();
  };

  const toggleSelect = (ip: string) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(ip)) next.delete(ip);
      else next.add(ip);
      return next;
    });
  };

  const handleRegister = async () => {
    if (state.status !== "DISCOVERED") return;
    setRegistering(true);
    try {
      const cameras = state.cameras
        .filter((c) => selected.has(c.ip_address))
        .map((c) => ({
          name: c.model ?? c.ip_address,
          ip_address: c.ip_address,
          rtsp_url: c.rtsp_url ?? undefined,
          onvif_port: c.port,
          manufacturer: c.manufacturer ?? undefined,
          model: c.model ?? undefined,
        }));
      await cameraApi.batchRegister({ cameras });
      onRegistered();
      handleClose();
    } finally {
      setRegistering(false);
    }
  };

  const handleClose = () => {
    reset();
    setSelected(new Set());
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="w-full max-w-lg rounded-lg bg-background p-6 shadow-xl">
        <h2 className="text-lg font-semibold">ONVIF 카메라 검색</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          네트워크에서 ONVIF 카메라를 자동 검색합니다
        </p>

        <div className="mt-4">
          <Button
            onClick={handleDiscover}
            disabled={state.status === "DISCOVERING"}
          >
            {state.status === "DISCOVERING" ? "검색 중..." : "검색 시작"}
          </Button>
        </div>

        {state.status === "DISCOVERED" && (
          <div className="mt-4 max-h-64 space-y-2 overflow-y-auto">
            {state.cameras.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                발견된 카메라가 없습니다
              </p>
            ) : (
              state.cameras.map((cam: DiscoveredCamera) => (
                <label
                  key={cam.ip_address}
                  className="flex cursor-pointer items-center gap-3 rounded border p-3 hover:bg-secondary/50"
                >
                  <input
                    type="checkbox"
                    checked={selected.has(cam.ip_address)}
                    onChange={() => toggleSelect(cam.ip_address)}
                    className="h-4 w-4"
                  />
                  <div className="flex-1">
                    <p className="text-sm font-medium">{cam.ip_address}</p>
                    <p className="text-xs text-muted-foreground">
                      {cam.manufacturer ?? "알 수 없음"}{" "}
                      {cam.model ? `- ${cam.model}` : ""}
                    </p>
                  </div>
                </label>
              ))
            )}
          </div>
        )}

        {state.status === "ERROR" && (
          <p className="mt-4 text-sm text-red-500">{state.message}</p>
        )}

        <div className="mt-6 flex justify-end gap-2">
          <Button variant="outline" onClick={handleClose}>
            닫기
          </Button>
          {state.status === "DISCOVERED" && selected.size > 0 && (
            <Button onClick={handleRegister} disabled={registering}>
              {registering
                ? "등록 중..."
                : `${selected.size}개 카메라 등록`}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
