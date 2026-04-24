import { http } from "@/infrastructure/http/httpClient";
import type { MediaServerScanResult } from "../../domain/model/mediaServer";

export const streamApi = {
  register: (cameraId: string, rtspUrl: string) =>
    http.post<{ stream_name: string; success: boolean }>("/api/streams", {
      camera_id: cameraId,
      rtsp_url: rtspUrl,
    }),

  unregister: (streamName: string) =>
    http.delete<{ stream_name: string; success: boolean }>(
      `/api/streams/${encodeURIComponent(streamName)}`,
    ),

  list: () =>
    http.get<{ streams: Record<string, unknown> }>("/api/streams"),

  webrtcOffer: (streamName: string, sdpOffer: string) =>
    http.post<{ sdp_answer: string }>("/api/streams/webrtc", {
      stream_name: streamName,
      sdp_offer: sdpOffer,
    }),

  scanMediaServers: (subnet: string) =>
    http.post<MediaServerScanResult>("/api/streams/media-servers/scan", {
      subnet,
    }),
};
