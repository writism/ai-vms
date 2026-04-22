"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { useIdentities } from "@/features/face/application/hooks/useIdentities";
import { IdentityCard } from "@/features/face/ui/components/IdentityCard";
import { RegisterIdentityDialog } from "@/features/face/ui/components/RegisterIdentityDialog";

export default function FacesPage() {
  const { identities, isLoading, refresh } = useIdentities();
  const [registerOpen, setRegisterOpen] = useState(false);

  return (
    <div>
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold">인물 관리</h2>
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
              <IdentityCard key={identity.id} identity={identity} />
            ))}
          </div>
        )}
      </div>

      <RegisterIdentityDialog
        open={registerOpen}
        onClose={() => setRegisterOpen(false)}
        onRegistered={() => refresh()}
      />
    </div>
  );
}
