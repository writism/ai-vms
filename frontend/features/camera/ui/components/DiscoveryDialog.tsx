"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { useCameraDiscovery } from "../../application/hooks/useCameraDiscovery";
import { cameraApi } from "../../infrastructure/api/cameraApi";
import type { DiscoveredCamera } from "../../domain/model/camera";

function EyeIcon({ open }: { open: boolean }) {
  if (open) {
    return (
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/>
        <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/>
        <line x1="1" y1="1" x2="23" y2="23"/>
      </svg>
    );
  }
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
      <circle cx="12" cy="12" r="3"/>
    </svg>
  );
}

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
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("");
  const [showPass, setShowPass] = useState(false);

  if (!open) return null;

  const cameras = state.status === "DISCOVERED" ? state.cameras : [];
  const allSelected = cameras.length > 0 && selected.size === cameras.length;

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

  const toggleAll = () => {
    if (allSelected) {
      setSelected(new Set());
    } else {
      setSelected(new Set(cameras.map((c) => c.ip_address)));
    }
  };

  const handleRegister = async () => {
    if (state.status !== "DISCOVERED") return;
    setRegistering(true);
    try {
      const toRegister = state.cameras
        .filter((c) => selected.has(c.ip_address))
        .map((c) => ({
          name: c.model ?? c.ip_address,
          ip_address: c.ip_address,
          rtsp_url: c.rtsp_url ?? undefined,
          onvif_port: c.port,
          manufacturer: c.manufacturer ?? undefined,
          model: c.model ?? undefined,
        }));
      const registered = await cameraApi.batchRegister({ cameras: toRegister });

      if (username && password) {
        await Promise.allSettled(
          registered.map((cam) =>
            cameraApi.fetchRtspUrl(cam.id, { username, password }),
          ),
        );
      }

      onRegistered();
      handleClose();
    } finally {
      setRegistering(false);
    }
  };

  const handleClose = () => {
    reset();
    setSelected(new Set());
    setUsername("admin");
    setPassword("");
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="w-full max-w-lg rounded-lg border bg-card p-6 shadow-xl">
        <h2 className="text-lg font-semibold">ONVIF 카메라 검색</h2>

        <div className="mt-3 flex items-center gap-2">
          <Button
            size="sm"
            onClick={handleDiscover}
            disabled={state.status === "DISCOVERING"}
          >
            {state.status === "DISCOVERING" ? "검색 중..." : "검색 시작"}
          </Button>
          {cameras.length > 0 && (
            <span className="text-xs text-muted-foreground">
              {cameras.length}개 발견 / {selected.size}개 선택
            </span>
          )}
        </div>

        {cameras.length > 0 && (
          <div className="mt-3 rounded border">
            <div className="flex items-center gap-2 border-b bg-muted/50 px-3 py-1.5">
              <input
                type="checkbox"
                checked={allSelected}
                onChange={toggleAll}
                className="h-3.5 w-3.5"
              />
              <span className="text-xs font-medium text-muted-foreground">전체 선택</span>
            </div>
            <div className="max-h-40 overflow-y-auto">
              {cameras.map((cam: DiscoveredCamera) => (
                <label
                  key={cam.ip_address}
                  className="flex cursor-pointer items-center gap-2 px-3 py-1.5 text-sm hover:bg-secondary/30 [&:not(:last-child)]:border-b"
                >
                  <input
                    type="checkbox"
                    checked={selected.has(cam.ip_address)}
                    onChange={() => toggleSelect(cam.ip_address)}
                    className="h-3.5 w-3.5"
                  />
                  <span className="font-mono text-xs">{cam.ip_address}</span>
                  <span className="truncate text-xs text-muted-foreground">
                    {cam.manufacturer ?? ""} {cam.model ?? ""}
                  </span>
                </label>
              ))}
            </div>
          </div>
        )}

        {cameras.length === 0 && state.status === "DISCOVERED" && (
          <p className="mt-3 text-sm text-muted-foreground">
            발견된 카메라가 없습니다
          </p>
        )}

        {state.status === "DISCOVERED" && selected.size > 0 && (
          <div className="mt-3 space-y-2 rounded border p-3">
            <p className="text-xs font-medium">인증 정보 (RTSP URL 자동 설정)</p>
            <div className="flex gap-2">
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="사용자명"
                className="w-1/2 rounded-md border bg-background px-3 py-1.5 text-sm"
              />
              <div className="relative w-1/2">
                <input
                  type={showPass ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="비밀번호"
                  className="w-full rounded-md border bg-background px-3 py-1.5 pr-8 text-sm"
                />
                <button
                  type="button"
                  onClick={() => setShowPass(!showPass)}
                  className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                  tabIndex={-1}
                >
                  <EyeIcon open={showPass} />
                </button>
              </div>
            </div>
          </div>
        )}

        {state.status === "ERROR" && (
          <p className="mt-3 text-sm text-red-500">{state.message}</p>
        )}

        <div className="mt-4 flex justify-end gap-2">
          <Button variant="outline" size="sm" onClick={handleClose}>
            닫기
          </Button>
          {state.status === "DISCOVERED" && selected.size > 0 && (
            <Button size="sm" onClick={handleRegister} disabled={registering}>
              {registering
                ? "등록 중..."
                : `${selected.size}개 등록`}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
