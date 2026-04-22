export interface Camera {
  id: string;
  name: string;
  ip_address: string;
  network_id: string | null;
  status: "ONLINE" | "OFFLINE" | "ERROR";
  rtsp_url: string | null;
  onvif_port: number;
  manufacturer: string | null;
  model: string | null;
  created_at: string;
}

export interface Network {
  id: string;
  name: string;
  subnet: string;
  description: string | null;
  is_active: boolean;
  created_at: string;
}

export interface DiscoveredCamera {
  ip_address: string;
  port: number;
  manufacturer: string | null;
  model: string | null;
  rtsp_url: string | null;
  onvif_address: string | null;
}
