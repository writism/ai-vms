import { http } from "@/infrastructure/http/httpClient";

export interface EventItem {
  id: string;
  event_type: string;
  camera_id: string | null;
  identity_id: string | null;
  description: string | null;
  created_at: string;
}

export interface EventList {
  items: EventItem[];
  total: number;
}

export const eventApi = {
  list: (params?: {
    event_type?: string;
    camera_id?: string;
    limit?: number;
    offset?: number;
  }) =>
    http.get<EventList>("/api/events", { params: params as Record<string, string> }),
};
