"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { cameraApi } from "../../infrastructure/api/cameraApi";
import type { DiscoveredCamera } from "../../domain/model/camera";

type Step = "form" | "confirm";

export function AddCameraByIpDialog({
  open,
  onClose,
  onRegistered,
}: {
  open: boolean;
  onClose: () => void;
  onRegistered: () => void;
}) {
  const [step, setStep] = useState<Step>("form");
  const [ip, setIp] = useState("");
  const [port, setPort] = useState("80");
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("");
  const [showPass, setShowPass] = useState(false);
  const [probing, setProbing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [probeResult, setProbeResult] = useState<DiscoveredCamera | null>(null);
  const [cameraName, setCameraName] = useState("");
  const [registering, setRegistering] = useState(false);

  const handleProbe = async () => {
    if (!ip.trim()) return;
    setProbing(true);
    setError(null);
    try {
      const result = await cameraApi.probe({
        ip_address: ip.trim(),
        port: parseInt(port, 10) || 80,
        username: username || undefined,
        password: password || undefined,
      });
      setProbeResult(result);
      setCameraName(result.model ?? result.ip_address);
      setStep("confirm");
    } catch {
      setError("연결할 수 없는 카메라입니다. IP·포트·계정을 확인하세요.");
    } finally {
      setProbing(false);
    }
  };

  const handleRegister = async () => {
    if (!probeResult) return;
    setRegistering(true);
    setError(null);
    try {
      const [registered] = await cameraApi.batchRegister({
        cameras: [
          {
            name: cameraName.trim() || probeResult.model || probeResult.ip_address,
            ip_address: probeResult.ip_address,
            rtsp_url: probeResult.rtsp_url ?? undefined,
            onvif_port: probeResult.port,
            manufacturer: probeResult.manufacturer ?? undefined,
            model: probeResult.model ?? undefined,
          },
        ],
      });
      if (username && password) {
        await cameraApi.fetchRtspUrl(registered.id, { username, password }).catch(() => null);
      }
      onRegistered();
      handleClose();
    } catch {
      setError("등록 중 오류가 발생했습니다.");
    } finally {
      setRegistering(false);
    }
  };

  const handleClose = () => {
    setStep("form");
    setIp("");
    setPort("80");
    setUsername("admin");
    setPassword("");
    setShowPass(false);
    setError(null);
    setProbeResult(null);
    setCameraName("");
    onClose();
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="w-full max-w-sm rounded-lg border bg-card p-6 shadow-xl">
        <h2 className="text-lg font-semibold">IP 직접 추가</h2>

        {step === "form" ? (
          <div className="mt-4 space-y-3">
            <div className="flex gap-2">
              <input
                type="text"
                value={ip}
                onChange={(e) => setIp(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleProbe()}
                placeholder="192.168.0.92"
                className="flex-1 rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
              />
              <input
                type="number"
                value={port}
                onChange={(e) => setPort(e.target.value)}
                placeholder="80"
                className="w-20 rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
              />
            </div>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="사용자명"
              className="w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
            />
            <div className="relative">
              <input
                type={showPass ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleProbe()}
                placeholder="비밀번호"
                className="w-full rounded-md border bg-background px-3 py-2 pr-9 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
              />
              <button
                type="button"
                onClick={() => setShowPass((v) => !v)}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                tabIndex={-1}
              >
                {showPass ? (
                  <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/><path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
                ) : (
                  <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                )}
              </button>
            </div>
            {error && <p className="text-sm text-red-500">{error}</p>}
            <div className="flex justify-end gap-2 pt-1">
              <Button variant="outline" size="sm" onClick={handleClose}>
                취소
              </Button>
              <Button size="sm" onClick={handleProbe} disabled={probing || !ip.trim()}>
                {probing ? "연결 중..." : "연결 확인"}
              </Button>
            </div>
          </div>
        ) : (
          <div className="mt-4 space-y-3">
            <div className="rounded-lg border bg-muted/40 px-4 py-3 text-sm space-y-1.5">
              <div className="flex justify-between">
                <span className="text-muted-foreground">IP</span>
                <span className="font-mono">{probeResult?.ip_address}</span>
              </div>
              {probeResult?.manufacturer && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">제조사</span>
                  <span>{probeResult.manufacturer}</span>
                </div>
              )}
              {probeResult?.model && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">모델</span>
                  <span>{probeResult.model}</span>
                </div>
              )}
              {probeResult?.rtsp_url && (
                <div className="flex justify-between gap-2">
                  <span className="shrink-0 text-muted-foreground">RTSP</span>
                  <span className="truncate font-mono text-xs text-muted-foreground">
                    {probeResult.rtsp_url}
                  </span>
                </div>
              )}
            </div>
            <div>
              <label className="text-xs text-muted-foreground">카메라 이름</label>
              <input
                type="text"
                value={cameraName}
                onChange={(e) => setCameraName(e.target.value)}
                className="mt-1 w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
              />
            </div>
            {error && <p className="text-sm text-red-500">{error}</p>}
            <div className="flex justify-end gap-2 pt-1">
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  setStep("form");
                  setError(null);
                }}
              >
                뒤로
              </Button>
              <Button size="sm" onClick={handleRegister} disabled={registering}>
                {registering ? "등록 중..." : "등록"}
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
