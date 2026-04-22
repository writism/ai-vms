import { http } from "@/infrastructure/http/httpClient";

export interface DangerEvent {
  id: string;
  camera_id: string;
  danger_type: string;
  severity: string;
  confidence: number;
  description: string | null;
  status: string;
  created_at: string;
}

export interface DangerEventList {
  items: DangerEvent[];
  total: number;
}

export const alertApi = {
  listEvents: (params?: {
    danger_type?: string;
    severity?: string;
    status?: string;
    limit?: number;
    offset?: number;
  }) =>
    http.get<DangerEventList>("/api/alerts/events", { params: params as Record<string, string> }),

  updateEventStatus: (eventId: string, data: { status: string; resolved_by?: string }) =>
    http.patch<DangerEvent>(`/api/alerts/events/${eventId}`, data),
};
