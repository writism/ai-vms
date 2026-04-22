"use client";

import { useAtom } from "jotai";
import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { authApi } from "../../infrastructure/api/authApi";
import { userAtom } from "../atoms/authAtoms";
import type { User } from "../../domain/model/auth";

export function useAuth() {
  const [user, setUser] = useAtom(userAtom);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      setLoading(false);
      return;
    }
    authApi
      .me()
      .then((data) => {
        setUser(data as User);
      })
      .catch(() => {
        localStorage.removeItem("access_token");
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, [setUser]);

  const login = useCallback(
    async (email: string, password: string) => {
      const res = await authApi.login({ email, password });
      localStorage.setItem("access_token", res.access_token);
      const me = await authApi.me();
      setUser(me as User);
      router.push("/");
    },
    [setUser, router],
  );

  const logout = useCallback(() => {
    localStorage.removeItem("access_token");
    setUser(null);
    router.push("/login");
  }, [setUser, router]);

  return { user, loading, login, logout };
}
