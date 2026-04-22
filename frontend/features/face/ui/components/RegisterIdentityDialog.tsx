"use client";

import { useState } from "react";
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
  const [type, setType] = useState("INTERNAL");
  const [department, setDepartment] = useState("");
  const [employeeId, setEmployeeId] = useState("");
  const [submitting, setSubmitting] = useState(false);

  if (!open) return null;

  const handleSubmit = async () => {
    if (!name.trim()) return;
    setSubmitting(true);
    try {
      await faceApi.registerIdentity({
        name: name.trim(),
        identity_type: type,
        department: department || undefined,
        employee_id: employeeId || undefined,
      });
      onRegistered();
      handleClose();
    } finally {
      setSubmitting(false);
    }
  };

  const handleClose = () => {
    setName("");
    setType("INTERNAL");
    setDepartment("");
    setEmployeeId("");
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="w-full max-w-md rounded-lg bg-background p-6 shadow-xl">
        <h2 className="text-lg font-semibold">인물 등록</h2>

        <div className="mt-4 space-y-3">
          <div>
            <label className="text-sm font-medium">이름 *</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="mt-1 w-full rounded border px-3 py-2 text-sm"
              placeholder="홍길동"
            />
          </div>
          <div>
            <label className="text-sm font-medium">유형</label>
            <select
              value={type}
              onChange={(e) => setType(e.target.value)}
              className="mt-1 w-full rounded border px-3 py-2 text-sm"
            >
              <option value="INTERNAL">내부인</option>
              <option value="EXTERNAL">외부인</option>
              <option value="VIP">VIP</option>
              <option value="BLACKLIST">블랙리스트</option>
            </select>
          </div>
          <div>
            <label className="text-sm font-medium">부서</label>
            <input
              type="text"
              value={department}
              onChange={(e) => setDepartment(e.target.value)}
              className="mt-1 w-full rounded border px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="text-sm font-medium">사번</label>
            <input
              type="text"
              value={employeeId}
              onChange={(e) => setEmployeeId(e.target.value)}
              className="mt-1 w-full rounded border px-3 py-2 text-sm"
            />
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
