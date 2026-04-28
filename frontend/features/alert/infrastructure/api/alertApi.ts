import { http } from "@/infrastructure/http/httpClient";

export interface DangerEvent {
  id: string;
  camera_id: string;
  danger_type: string;
  severity: string;
  confidence: number;
  description: string | null;
  snapshot_path: string | null;
  status: string;
  resolved_by: string | null;
  resolved_at: string | null;
  created_at: string;
}

export interface DangerEventList {
  items: DangerEvent[];
  total: number;
}

export interface AlertRule {
  id: string;
  name: string;
  danger_types: string[];
  min_severity: string;
  notify_websocket: boolean;
  notify_mqtt: boolean;
  notify_email: boolean;
  email_recipients: string[];
  enable_face_recognition: boolean;
  is_active: boolean;
  created_at: string;
}

export interface CreateAlertRuleRequest {
  name: string;
  danger_types: string[];
  min_severity: string;
  notify_websocket?: boolean;
  notify_mqtt?: boolean;
  notify_email?: boolean;
  email_recipients?: string[];
  enable_face_recognition?: boolean;
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

  listRules: () => http.get<AlertRule[]>("/api/alerts/rules"),

  createRule: (data: CreateAlertRuleRequest) =>
    http.post<AlertRule>("/api/alerts/rules", data),

  deleteRule: (ruleId: string) =>
    http.delete<void>(`/api/alerts/rules/${ruleId}`),
};
