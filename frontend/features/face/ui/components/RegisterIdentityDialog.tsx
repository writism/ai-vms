"use client";

import { useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { faceApi } from "../../infrastructure/api/faceApi";

export function RegisterIdentityDialog({
  open,
  onClose,
  onRegistered,
}: {
  open: boolean;
  onClose: () => void;
  onRegistered: () => void;
}) {
  const [name, setName] = useState("");
  const [type, setType] = useState("EMPLOYEE");
  const [department, setDepartment] = useState("");
  const [employeeId, setEmployeeId] = useState("");
  const [company, setCompany] = useState("");
  const [visitPurpose, setVisitPurpose] = useState("");
  const [photoFile, setPhotoFile] = useState<File | null>(null);
  const [photoPreview, setPhotoPreview] = useState<string | null>(null);
  const [webcamActive, setWebcamActive] = useState(false);
  const [webcamError, setWebcamError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const dialogRef = useRef<HTMLDivElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  useEffect(() => {
    if (!open) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") handleClose();
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [open]);

  useEffect(() => {
    return () => stopWebcam();
  }, []);

  const startWebcam = async () => {
    setWebcamError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "user", width: 640, height: 480 } });
      streamRef.current = stream;
      setWebcamActive(true);
    } catch (e) {
      const msg = e instanceof DOMException && e.name === "NotAllowedError"
        ? "카메라 권한이 거부되었습니다"
        : "카메라에 접근할 수 없습니다 (HTTPS 필요)";
      setWebcamError(msg);
    }
  };

  const stopWebcam = () => {
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
    setWebcamActive(false);
  };

  const captureWebcam = () => {
    const video = videoRef.current;
    if (!video || video.videoWidth === 0) return;
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext("2d")!.drawImage(video, 0, 0);
    const dataUrl = canvas.toDataURL("image/jpeg", 0.9);
    fetch(dataUrl)
      .then((res) => res.blob())
      .then((blob) => {
        const file = new File([blob], "webcam-capture.jpg", { type: "image/jpeg" });
        setPhotoFile(file);
        setPhotoPreview(dataUrl);
        stopWebcam();
      });
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setPhotoFile(file);
    setPhotoPreview(URL.createObjectURL(file));
    stopWebcam();
  };

  if (!open) return null;

  const handleSubmit = async () => {
    if (!name.trim()) return;
    setSubmitting(true);
    try {
      const identity = await faceApi.registerIdentity({
        name: name.trim(),
        identity_type: type,
        department: type === "EMPLOYEE" ? department || undefined : undefined,
        employee_id: type === "EMPLOYEE" ? employeeId || undefined : undefined,
        company: type === "VISITOR" ? company || undefined : undefined,
        visit_purpose: type === "VISITOR" ? visitPurpose || undefined : undefined,
      });
      if (photoFile && identity?.id) {
        await faceApi.uploadFacePhoto(identity.id, photoFile);
      }
      onRegistered();
      handleClose();
    } finally {
      setSubmitting(false);
    }
  };

  const handleClose = () => {
    setName("");
    setType("EMPLOYEE");
    setDepartment("");
    setEmployeeId("");
    setCompany("");
    setVisitPurpose("");
    setPhotoFile(null);
    setPhotoPreview(null);
    stopWebcam();
    onClose();
  };

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (dialogRef.current && !dialogRef.current.contains(e.target as Node)) {
      handleClose();
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      onClick={handleBackdropClick}
    >
      <div
        ref={dialogRef}
        className="w-full max-w-lg rounded-xl border border-border bg-card p-6 shadow-2xl"
      >
        <h2 className="text-lg font-semibold">인물 등록</h2>

        <div className="mt-4 space-y-3">
          <div>
            <label className="text-sm font-medium">이름 *</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="mt-1 w-full rounded-md border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="홍길동"
            />
          </div>
          <div>
            <label className="text-sm font-medium">유형</label>
            <select
              value={type}
              onChange={(e) => setType(e.target.value)}
              className="mt-1 w-full rounded-md border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="EMPLOYEE">임직원</option>
              <option value="VISITOR">방문객</option>
            </select>
          </div>

          {type === "EMPLOYEE" && (
            <>
              <div>
                <label className="text-sm font-medium">부서</label>
                <input
                  type="text"
                  value={department}
                  onChange={(e) => setDepartment(e.target.value)}
                  className="mt-1 w-full rounded-md border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>
              <div>
                <label className="text-sm font-medium">사번</label>
                <input
                  type="text"
                  value={employeeId}
                  onChange={(e) => setEmployeeId(e.target.value)}
                  className="mt-1 w-full rounded-md border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>
            </>
          )}

          {type === "VISITOR" && (
            <>
              <div>
                <label className="text-sm font-medium">소속 (회사명)</label>
                <input
                  type="text"
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  className="mt-1 w-full rounded-md border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>
              <div>
                <label className="text-sm font-medium">방문 목적</label>
                <input
                  type="text"
                  value={visitPurpose}
                  onChange={(e) => setVisitPurpose(e.target.value)}
                  className="mt-1 w-full rounded-md border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>
            </>
          )}

          <div>
            <label className="text-sm font-medium">얼굴 사진</label>
            <div className="mt-1 space-y-2">
              {webcamActive ? (
                <div className="space-y-2">
                  <video
                    ref={(el) => {
                      videoRef.current = el;
                      if (el && streamRef.current) {
                        el.srcObject = streamRef.current;
                      }
                    }}
                    autoPlay
                    playsInline
                    muted
                    className="w-full rounded-md border border-border"
                  />
                  <div className="flex gap-2">
                    <Button type="button" onClick={captureWebcam} className="flex-1">
                      촬영
                    </Button>
                    <Button type="button" variant="outline" onClick={stopWebcam} className="flex-1">
                      취소
                    </Button>
                  </div>
                </div>
              ) : photoPreview ? (
                <div className="relative">
                  <img src={photoPreview} alt="미리보기" className="w-full rounded-md border border-border" />
                  <button
                    type="button"
                    onClick={() => { setPhotoFile(null); setPhotoPreview(null); }}
                    className="absolute right-2 top-2 rounded-full bg-black/60 px-2 py-0.5 text-xs text-white hover:bg-black/80"
                  >
                    삭제
                  </button>
                </div>
              ) : (
                <div className="space-y-2">
                {webcamError && (
                  <p className="text-xs text-red-400">{webcamError}</p>
                )}
                <div className="flex gap-2">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={startWebcam}
                    className="flex-1"
                  >
                    웹캠 촬영
                  </Button>
                  <label className="flex flex-1 cursor-pointer items-center justify-center rounded-md border border-border bg-background px-3 py-2 text-sm hover:bg-muted">
                    사진 업로드
                    <input
                      type="file"
                      accept="image/jpeg,image/png"
                      onChange={handleFileSelect}
                      className="hidden"
                    />
                  </label>
                </div>
              </div>
              )}
            </div>
          </div>
        </div>

        <div className="mt-6 flex justify-end gap-2">
          <Button variant="outline" onClick={handleClose}>
            취소
          </Button>
          <Button onClick={handleSubmit} disabled={submitting || !name.trim()}>
            {submitting ? "등록 중..." : "등록"}
          </Button>
        </div>
      </div>
    </div>
  );
}
