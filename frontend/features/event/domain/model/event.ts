export interface Event {
  id: string;
  event_type: EventType;
  camera_id: string | null;
  identity_id: string | null;
  danger_event_id: string | null;
  description: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
}

export type EventType =
  | "FACE_RECOGNIZED"
  | "FACE_UNIDENTIFIED"
  | "DANGER_DETECTED"
  | "CAMERA_ONLINE"
  | "CAMERA_OFFLINE"
  | "ACCESS_GRANTED"
  | "ACCESS_DENIED";
