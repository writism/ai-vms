import { http } from "@/infrastructure/http/httpClient";

export const streamApi = {
  register: (cameraId: string, rtspUrl: string) =>
    http.post<{ stream_name: string; success: boolean }>("/api/streams", {
      camera_id: cameraId,
      rtsp_url: rtspUrl,
    }),

  list: () =>
    http.get<{ streams: Record<string, unknown> }>("/api/streams"),

  webrtcOffer: (streamName: string, sdpOffer: string) =>
    http.post<{ sdp_answer: string }>("/api/streams/webrtc", {
      stream_name: streamName,
      sdp_offer: sdpOffer,
    }),
};
