export const env = {
  apiUrl: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000",
  wsUrl: process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000",
  go2rtcUrl: process.env.NEXT_PUBLIC_GO2RTC_URL ?? "http://localhost:1984",
} as const;
