export interface StreamSession {
  stream_name: string;
  camera_id: string;
  rtsp_url: string;
  status: StreamStatus;
}

export type StreamStatus = "ACTIVE" | "INACTIVE" | "ERROR";
