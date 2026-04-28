import { http } from "@/infrastructure/http/httpClient";
import { env } from "@/infrastructure/config/env";
import type { Identity, RecognitionLog } from "../../domain/model/face";

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

  uploadFacePhoto: async (identityId: string, file: File) => {
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
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
    return res.json();
  },
};
