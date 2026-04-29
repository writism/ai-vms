"use client";

import { useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { faceApi } from "../../infrastructure/api/faceApi";
import { humanizeMediaError } from "../lib/media-error";

export function RegisterIdentityDialog({
  open,
  onClose,
  onRegistered,
  prefilledPhotoUrl,
  clusterId,
}: {
  open: boolean;
  onClose: () => void;
  onRegistered: () => void;
  prefilledPhotoUrl?: string | null;
  clusterId?: string | null;
}) {
  const [name, setName] = useState("");
  const [type, setType] = useState("EMPLOYEE");
  const [department, setDepartment] = useState("");
  const [employeeId, setEmployeeId] = useState("");
  const [company, setCompany] = useState("");
  const [visitPurpose, setVisitPurpose] = useState("");
  const [photoFile, setPhotoFile] = useState<File | null>(null);
  const [photoPreview, setPhotoPreview] = useState<string | null>(prefilledPhotoUrl ?? null);
  const [webcamActive, setWebcamActive] = useState(false);
  const [webcamError, setWebcamError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [createdIdentityId, setCreatedIdentityId] = useState<string | null>(null);
  const [embeddingWarning, setEmbeddingWarning] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
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
    if (open && prefilledPhotoUrl && !photoPreview && !photoFile) {
      setPhotoPreview(prefilledPhotoUrl);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, prefilledPhotoUrl]);

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
      setWebcamError(humanizeMediaError(e));
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
        setEmbeddingWarning(null);
        setUploadError(null);
        stopWebcam();
      });
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setPhotoFile(file);
    setPhotoPreview(URL.createObjectURL(file));
    setEmbeddingWarning(null);
    setUploadError(null);
    stopWebcam();
  };

  if (!open) return null;

  const handleSubmit = async () => {
    if (!name.trim()) return;
    setSubmitting(true);
    setUploadError(null);
    setEmbeddingWarning(null);
    try {
      let identityId = createdIdentityId;
      if (!identityId) {
        const identity = await faceApi.registerIdentity({
          name: name.trim(),
          identity_type: type,
          department: type === "EMPLOYEE" ? department || undefined : undefined,
          employee_id: type === "EMPLOYEE" ? employeeId || undefined : undefined,
          company: type === "VISITOR" ? company || undefined : undefined,
          visit_purpose: type === "VISITOR" ? visitPurpose || undefined : undefined,
        });
        identityId = identity.id;
        setCreatedIdentityId(identityId);
      }
      if (photoFile) {
        try {
          const result = await faceApi.uploadFacePhoto(identityId, photoFile);
          if (!result.has_embedding) {
            setEmbeddingWarning(
              "얼굴이 검출되지 않았습니다. 정면이 선명하게 보이는 다른 사진으로 다시 시도하세요.",
            );
            onRegistered();
            return;
          }
        } catch (e) {
          setUploadError(e instanceof Error ? e.message : "사진 업로드에 실패했습니다");
          onRegistered();
          return;
        }
      }
      if (clusterId) {
        try {
          await faceApi.registerSuggestion(clusterId, identityId);
        } catch (e) {
          console.warn("cluster register failed:", e);
        }
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
    setCreatedIdentityId(null);
    setEmbeddingWarning(null);
    setUploadError(null);
    setWebcamError(null);
    stopWebcam();
    onClose();
  };

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (dialogRef.current && !dialogRef.current.contains(e.target as Node)) {
      handleClose();
    }
  };

  const identityLocked = createdIdentityId !== null;
  const submitLabel = submitting
    ? "등록 중..."
    : identityLocked
      ? "사진 다시 시도"
      : "등록";

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

        {identityLocked && (
          <p className="mt-2 text-xs text-muted-foreground">
            인물 정보는 이미 등록되었습니다. 사진만 다시 선택하면 검출을 재시도합니다.
          </p>
        )}

        <div className="mt-4 space-y-3">
          <div>
            <label className="text-sm font-medium">이름 *</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              disabled={identityLocked}
              className="mt-1 w-full rounded-md border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-60"
              placeholder="홍길동"
            />
          </div>
          <div>
            <label className="text-sm font-medium">유형</label>
            <select
              value={type}
              onChange={(e) => setType(e.target.value)}
              disabled={identityLocked}
              className="mt-1 w-full rounded-md border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-60"
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
                  disabled={identityLocked}
                  className="mt-1 w-full rounded-md border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-60"
                />
              </div>
              <div>
                <label className="text-sm font-medium">사번</label>
                <input
                  type="text"
                  value={employeeId}
                  onChange={(e) => setEmployeeId(e.target.value)}
                  disabled={identityLocked}
                  className="mt-1 w-full rounded-md border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-60"
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
                  disabled={identityLocked}
                  className="mt-1 w-full rounded-md border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-60"
                />
              </div>
              <div>
                <label className="text-sm font-medium">방문 목적</label>
                <input
                  type="text"
                  value={visitPurpose}
                  onChange={(e) => setVisitPurpose(e.target.value)}
                  disabled={identityLocked}
                  className="mt-1 w-full rounded-md border border-border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-60"
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
                    onClick={() => {
                      setPhotoFile(null);
                      setPhotoPreview(null);
                      setEmbeddingWarning(null);
                      setUploadError(null);
                    }}
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
              {embeddingWarning && (
                <p className="rounded border border-amber-300 bg-amber-50 px-3 py-2 text-xs text-amber-800 dark:border-amber-800 dark:bg-amber-950 dark:text-amber-300">
                  {embeddingWarning}
                </p>
              )}
              {uploadError && (
                <p className="text-xs text-red-500">{uploadError}</p>
              )}
            </div>
          </div>
        </div>

        <div className="mt-6 flex justify-end gap-2">
          <Button variant="outline" onClick={handleClose}>
            {identityLocked ? "닫기" : "취소"}
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={submitting || !name.trim() || (identityLocked && !photoFile)}
          >
            {submitLabel}
          </Button>
        </div>
      </div>
    </div>
  );
}
