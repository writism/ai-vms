import { http } from "@/infrastructure/http/httpClient";
import type { Camera, DiscoveredCamera, Network } from "../../domain/model/camera";

export const cameraApi = {
  list: () => http.get<Camera[]>("/api/cameras"),

  get: (id: string) => http.get<Camera>(`/api/cameras/${id}`),

  register: (data: {
    name: string;
    ip_address: string;
    network_id?: string;
    rtsp_url?: string;
    onvif_port?: number;
  }) => http.post<Camera>("/api/cameras", data),

  discover: (timeout = 3.0) =>
    http.post<DiscoveredCamera[]>("/api/cameras/discover", { timeout }),

  update: (
    id: string,
    data: {
      name?: string;
      rtsp_url?: string;
      onvif_port?: number;
      manufacturer?: string;
      model?: string;
    },
  ) => http.patch<Camera>(`/api/cameras/${id}`, data),

  fetchRtspUrl: (id: string, data: { username: string; password: string }) =>
    http.post<Camera>(`/api/cameras/${id}/fetch-rtsp`, data),

  batchRegister: (data: {
    network_id?: string;
    cameras: {
      name: string;
      ip_address: string;
      rtsp_url?: string;
      onvif_port?: number;
      manufacturer?: string;
      model?: string;
    }[];
  }) => http.post<Camera[]>("/api/cameras/batch", data),
};

export const networkApi = {
  list: () => http.get<Network[]>("/api/networks"),

  register: (data: { name: string; subnet: string; description?: string }) =>
    http.post<Network>("/api/networks", data),
};
