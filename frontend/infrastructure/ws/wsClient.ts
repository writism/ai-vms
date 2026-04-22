import { env } from "@/infrastructure/config/env";

export function createWsConnection(path: string): WebSocket {
  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
  const url = `${env.wsUrl}${path}${token ? `?token=${token}` : ""}`;
  return new WebSocket(url);
}
