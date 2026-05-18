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

export interface ClusterSnapshot {
  log_id: string;
  image_url: string;
  confidence: number;
  created_at: string;
}

export interface SimilarIdentity {
  identity_id: string;
  name: string;
  position: string | null;
  department: string | null;
  identity_type: string;
  face_image_url: string | null;
  score: number;
}

export interface FaceDetail {
  face_id: string;
  image_url: string | null;
  quality_score: number;
  created_at: string;
  is_outlier: boolean;
}

export interface OutlierSnapshot {
  log_id: string;
  image_url: string;
  confidence: number;
  created_at: string;
  is_outlier: boolean;
  similarity_to_mean: number;
}

export const faceApi = {
  listIdentities: () => http.get<Identity[]>("/api/faces/identities"),

  getIdentity: (id: string) => http.get<Identity>(`/api/faces/identities/${id}`),

  registerIdentity: (data: {
    name: string;
    identity_type?: string;
    department?: string;
    employee_id?: string;
    position?: string;
    company?: string;
    visit_purpose?: string;
    notes?: string;
  }) => http.post<Identity>("/api/faces/identities", data),

  updateIdentity: (id: string, data: {
    name?: string;
    identity_type?: string;
    department?: string;
    employee_id?: string;
    position?: string;
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

  getClusterSnapshots: (clusterId: string, limit = 50) =>
    http.get<ClusterSnapshot[]>(`/api/faces/clusters/${clusterId}/snapshots`, {
      params: { limit: String(limit) },
    }),

  matchRecognitionLog: (logId: string, limit = 5) =>
    http.get<SimilarIdentity[]>(`/api/faces/recognition-logs/${logId}/match`, {
      params: { limit: String(limit) },
    }),

  assignRecognitionLog: (logId: string, identityId: string) =>
    http.post<{ assigned: number; identity_name: string }>(
      `/api/faces/recognition-logs/${logId}/assign`,
      undefined,
      { params: { identity_id: identityId } },
    ),

  deleteClusterSnapshot: (clusterId: string, logId: string) =>
    http.delete(`/api/faces/clusters/${clusterId}/snapshots/${logId}`),

  getClusterOutliers: (clusterId: string, threshold = 0.75) =>
    http.get<OutlierSnapshot[]>(`/api/faces/clusters/${clusterId}/outliers`, {
      params: { threshold: String(threshold) },
    }),

  listIdentityFaces: (identityId: string) =>
    http.get<FaceDetail[]>(`/api/faces/identities/${identityId}/faces`),

  deleteIdentityFace: (identityId: string, faceId: string) =>
    http.delete(`/api/faces/identities/${identityId}/faces/${faceId}`),

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
