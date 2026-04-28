"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { useIdentities } from "@/features/face/application/hooks/useIdentities";
import { IdentityCard } from "@/features/face/ui/components/IdentityCard";
import { RegisterIdentityDialog } from "@/features/face/ui/components/RegisterIdentityDialog";
import { EditIdentityDialog } from "@/features/face/ui/components/EditIdentityDialog";
import { RecognitionLogList } from "@/features/face/ui/components/RecognitionLogList";
import type { Identity } from "@/features/face/domain/model/face";

export default function FacesPage() {
  const { identities, isLoading, refresh } = useIdentities();
  const [registerOpen, setRegisterOpen] = useState(false);
  const [editTarget, setEditTarget] = useState<Identity | null>(null);

  return (
    <div>
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold">출입 관리</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            {identities.length}명 등록됨
          </p>
        </div>
        <Button onClick={() => setRegisterOpen(true)}>인물 등록</Button>
      </div>

      <div className="mt-6">
        {isLoading ? (
          <div className="flex h-48 items-center justify-center text-muted-foreground">
            로딩 중...
          </div>
        ) : identities.length === 0 ? (
          <div className="flex h-48 items-center justify-center text-muted-foreground">
            등록된 인물이 없습니다
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {identities.map((identity) => (
              <IdentityCard key={identity.id} identity={identity} onClick={() => setEditTarget(identity)} />
            ))}
          </div>
        )}
      </div>

      <div className="mt-8">
        <h3 className="text-lg font-semibold">인식 로그</h3>
        <p className="mt-1 text-sm text-muted-foreground">
          카메라에서 검출된 인물 인식 이력
        </p>
        <div className="mt-4">
          <RecognitionLogList />
        </div>
      </div>

      <RegisterIdentityDialog
        open={registerOpen}
        onClose={() => setRegisterOpen(false)}
        onRegistered={() => refresh()}
      />

      {editTarget && (
        <EditIdentityDialog
          identity={editTarget}
          onClose={() => setEditTarget(null)}
          onUpdated={() => refresh()}
        />
      )}
    </div>
  );
}
