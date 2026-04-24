"use client";

import { useState } from "react";
import { useMediaServers } from "../../application/hooks/useMediaServers";
import type { MediaServer } from "@/features/stream/domain/model/mediaServer";
import { cn } from "@/lib/utils";

const DEFAULT_SUBNET = "192.168.0.0/23";

function ServerCard({ server }: { server: MediaServer }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="rounded border bg-card">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex w-full items-center justify-between px-3 py-2 text-left text-sm hover:bg-muted/50"
      >
        <div className="flex items-center gap-2">
          <span
            className={cn(
              "h-2 w-2 rounded-full",
              server.reachable ? "bg-green-500" : "bg-gray-400",
            )}
          />
          <span className="font-mono font-medium">{server.ip}:{server.port}</span>
          {server.is_own && (
            <span className="rounded bg-blue-100 px-1.5 py-0.5 text-xs text-blue-700">
              내 서버
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-muted-foreground">
            스트림 {server.streams.length}개
          </span>
          <span className="text-xs">{expanded ? "▲" : "▼"}</span>
        </div>
      </button>
      {expanded && server.streams.length > 0 && (
        <div className="border-t px-3 py-2">
          <table className="w-full text-xs">
            <thead>
              <tr className="text-muted-foreground">
                <th className="py-1 text-left font-medium">스트림</th>
                <th className="py-1 text-left font-medium">카메라 IP</th>
              </tr>
            </thead>
            <tbody>
              {server.streams.map((s) => (
                <tr key={s.name} className="border-t border-dashed">
                  <td className="py-1 font-mono">{s.name}</td>
                  <td className="py-1 font-mono">
                    {s.camera_ip ?? "-"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {expanded && server.streams.length === 0 && (
        <div className="border-t px-3 py-2 text-xs text-muted-foreground">
          등록된 스트림 없음
        </div>
      )}
    </div>
  );
}

export function MediaServerSection() {
  const { data, isScanning, error, scan } = useMediaServers();
  const [collapsed, setCollapsed] = useState(false);
  const [subnet, setSubnet] = useState(DEFAULT_SUBNET);

  return (
    <div className="rounded-lg border bg-card">
      <div className="flex items-center justify-between border-b px-4 py-3">
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="flex items-center gap-2 font-semibold"
        >
          <span className="text-xs">{collapsed ? "▶" : "▼"}</span>
          네트워크 미디어 서버
          {data && data.conflicts.length > 0 && (
            <span className="rounded-full bg-orange-100 px-2 py-0.5 text-xs font-medium text-orange-700">
              충돌 {data.conflicts.length}
            </span>
          )}
        </button>
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={subnet}
            onChange={(e) => setSubnet(e.target.value)}
            className="w-40 rounded border px-2 py-1 text-xs font-mono"
            placeholder="서브넷 (예: 192.168.0.0/24)"
          />
          <button
            onClick={() => scan(subnet)}
            disabled={isScanning}
            className={cn(
              "rounded px-3 py-1 text-xs font-medium text-white",
              isScanning
                ? "cursor-not-allowed bg-gray-400"
                : "bg-blue-600 hover:bg-blue-700",
            )}
          >
            {isScanning ? "스캔 중..." : "스캔"}
          </button>
        </div>
      </div>

      {!collapsed && (
        <div className="p-4">
          {error && (
            <div className="mb-3 rounded bg-red-50 px-3 py-2 text-sm text-red-700">
              {error}
            </div>
          )}

          {!data && !isScanning && !error && (
            <p className="text-sm text-muted-foreground">
              서브넷을 입력하고 스캔 버튼을 눌러 네트워크 내 미디어 서버를 검색하세요.
            </p>
          )}

          {isScanning && (
            <p className="text-sm text-muted-foreground">
              네트워크를 스캔하고 있습니다...
            </p>
          )}

          {data && !isScanning && (
            <div className="space-y-4">
              {data.conflicts.length > 0 && (
                <div className="rounded bg-orange-50 px-3 py-2">
                  <p className="text-sm font-medium text-orange-800">
                    카메라 연결 충돌 감지
                  </p>
                  <ul className="mt-1 space-y-1">
                    {data.conflicts.map((c) => (
                      <li key={c.camera_ip} className="text-xs text-orange-700">
                        <span className="font-mono font-medium">{c.camera_ip}</span>
                        {" → "}
                        {c.servers.map((s) => (
                          <span key={s} className="font-mono">{s}</span>
                        )).reduce((prev, curr) => (
                          <>{prev}, {curr}</>
                        ))}
                        {" "}
                        ({c.servers.length}개 서버에 동시 연결)
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {data.servers.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  발견된 미디어 서버가 없습니다.
                </p>
              ) : (
                <div className="space-y-2">
                  <p className="text-xs text-muted-foreground">
                    {data.servers.length}개 서버 발견
                  </p>
                  {data.servers.map((server) => (
                    <ServerCard key={server.ip} server={server} />
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
