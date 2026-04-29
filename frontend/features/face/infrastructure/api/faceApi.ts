import { http } from "@/infrastructure/http/httpClient";
import { env } from "@/infrastructure/config/env";
import type { Identity, RecognitionLog } from "../../domain/model/face";

export interface UploadFacePhotoResponse {
  status: string;
  image_path: string;
  has_embedding: boolean;
}

export interface FaceSuggestion {
  cluster_id: string;
  image_url: string | null;
  count_window: number;
  avg_confidence: number;
  last_seen: string;
  last_camera_id: string | null;
  quality_score: number;
  status: string;
}

export const faceApi = {
  listIdentities: () => http.get<Identity[]>("/api/faces/identities"),

  getIdentity: (id: string) => http.get<Identity>(`/api/faces/identities/${id}`),

  registerIdentity: (data: {
    name: string;
    identity_type?: string;
    department?: string;
    employee_id?: string;
    company?: string;
    visit_purpose?: string;
    notes?: string;
  }) => http.post<Identity>("/api/faces/identities", data),

  updateIdentity: (id: string, data: {
    name?: string;
    identity_type?: string;
    department?: string;
    employee_id?: string;
    company?: string;
    visit_purpose?: string;
    notes?: string;
  }) => http.put<Identity>(`/api/faces/identities/${id}`, data),

  deleteIdentity: (id: string) => http.delete(`/api/faces/identities/${id}`),

  listRecognitionLogs: (limit = 20) =>
    http.get<RecognitionLog[]>(`/api/faces/recognition-logs`, { params: { limit: String(limit) } }),

  listSuggestions: () => http.get<FaceSuggestion[]>("/api/faces/suggestions"),

  registerSuggestion: (clusterId: string, identityId: string) =>
    http.post(`/api/faces/suggestions/${clusterId}/register`, undefined, {
      params: { identity_id: identityId },
    }),

  ignoreSuggestion: (clusterId: string) =>
    http.post(`/api/faces/suggestions/${clusterId}/ignore`),

  uploadFacePhoto: async (identityId: string, file: File): Promise<UploadFacePhotoResponse> => {
    const formData = new FormData();
    formData.append("file", file);
    const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
    const headers: Record<string, string> = {};
    if (token) headers["Authorization"] = `Bearer ${token}`;
    const res = await fetch(`${env.apiUrl}/api/faces/identities/${identityId}/photo`, {
      method: "POST",
      headers,
      body: formData,
    });
    if (!res.ok) {
      const body = await res.text();
      throw new Error(`${res.status} ${res.statusText}: ${body}`);
    }
    return res.json();
  },
};
