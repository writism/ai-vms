"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { useIdentities } from "@/features/face/application/hooks/useIdentities";
import { useFaceSuggestions } from "@/features/face/application/hooks/useFaceSuggestions";
import { IdentityCard } from "@/features/face/ui/components/IdentityCard";
import { FaceSuggestionCard } from "@/features/face/ui/components/FaceSuggestionCard";
import { RegisterIdentityDialog } from "@/features/face/ui/components/RegisterIdentityDialog";
import { EditIdentityDialog } from "@/features/face/ui/components/EditIdentityDialog";
import { RecognitionLogList } from "@/features/face/ui/components/RecognitionLogList";
import type { Identity } from "@/features/face/domain/model/face";
import { env } from "@/infrastructure/config/env";
import type { FaceSuggestion } from "@/features/face/infrastructure/api/faceApi";

export default function FacesPage() {
  const { identities, isLoading, refresh } = useIdentities();
  const { suggestions, refresh: refreshSuggestions } = useFaceSuggestions();
  const [registerOpen, setRegisterOpen] = useState(false);
  const [registerSeed, setRegisterSeed] = useState<{
    photoUrl: string | null;
    clusterId: string | null;
  } | null>(null);
  const [editTarget, setEditTarget] = useState<Identity | null>(null);

  const openRegisterFor = (s: FaceSuggestion) => {
    setRegisterSeed({
      photoUrl: s.image_url ? `${env.apiUrl}${s.image_url}` : null,
      clusterId: s.cluster_id,
    });
    setRegisterOpen(true);
  };
  const openEmptyRegister = () => {
    setRegisterSeed(null);
    setRegisterOpen(true);
  };
  const handleRegistered = () => {
    refresh();
    refreshSuggestions();
  };
  const closeRegister = () => {
    setRegisterOpen(false);
    setRegisterSeed(null);
  };

  return (
    <div>
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold">출입 관리</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            {identities.length}명 등록됨
          </p>
        </div>
        <Button onClick={openEmptyRegister}>인물 등록</Button>
      </div>

      {suggestions.length > 0 && (
        <div className="mt-6 rounded-lg border border-amber-300 bg-amber-50/40 p-4 dark:border-amber-800 dark:bg-amber-950/20">
          <div className="mb-3 flex items-center justify-between">
            <div>
              <h3 className="text-base font-semibold text-amber-900 dark:text-amber-200">
                등록 추천
              </h3>
              <p className="text-xs text-amber-800 dark:text-amber-300">
                최근 24시간 내 자주 등장한 미등록 얼굴 후보 ({suggestions.length}건). 본인이 맞으면 등록하세요.
              </p>
            </div>
          </div>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {suggestions.map((s) => (
              <FaceSuggestionCard
                key={s.cluster_id}
                suggestion={s}
                onRegister={openRegisterFor}
                onResolved={refreshSuggestions}
              />
            ))}
          </div>
        </div>
      )}

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
        onClose={closeRegister}
        onRegistered={handleRegistered}
        prefilledPhotoUrl={registerSeed?.photoUrl ?? null}
        clusterId={registerSeed?.clusterId ?? null}
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
