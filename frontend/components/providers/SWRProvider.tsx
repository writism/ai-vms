"use client";

import { SWRConfig } from "swr";
import { http } from "@/infrastructure/http/httpClient";

export function SWRProvider({ children }: { children: React.ReactNode }) {
  return (
    <SWRConfig
      value={{
        fetcher: (url: string) => http.get(url),
        revalidateOnFocus: false,
      }}
    >
      {children}
    </SWRConfig>
  );
}
