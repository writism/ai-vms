export interface MediaServerStream {
  name: string;
  url: string;
  camera_ip: string | null;
}

export interface MediaServer {
  ip: string;
  port: number;
  reachable: boolean;
  streams: MediaServerStream[];
  is_own: boolean;
}

export interface CameraConflict {
  camera_ip: string;
  servers: string[];
}

export interface MediaServerScanResult {
  servers: MediaServer[];
  conflicts: CameraConflict[];
  own_server_ip: string | null;
}
