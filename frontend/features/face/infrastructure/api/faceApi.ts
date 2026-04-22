import { http } from "@/infrastructure/http/httpClient";
import type { Identity } from "../../domain/model/face";

export const faceApi = {
  listIdentities: () => http.get<Identity[]>("/api/faces/identities"),

  getIdentity: (id: string) => http.get<Identity>(`/api/faces/identities/${id}`),

  registerIdentity: (data: {
    name: string;
    identity_type?: string;
    department?: string;
    employee_id?: string;
    notes?: string;
  }) => http.post<Identity>("/api/faces/identities", data),
};
