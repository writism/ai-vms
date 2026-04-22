export interface DangerEvent {
  id: string;
  danger_type: DangerType;
  severity: Severity;
  status: DangerEventStatus;
  camera_id: string;
  confidence: number;
  snapshot_url: string | null;
  description: string | null;
  acknowledged_by: string | null;
  acknowledged_at: string | null;
  created_at: string;
}

export type DangerType =
  | "FIRE"
  | "SMOKE"
  | "VIOLENCE"
  | "FIGHT"
  | "WEAPON"
  | "FALL"
  | "INTRUSION";

export type Severity = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export type DangerEventStatus = "PENDING" | "ACKNOWLEDGED" | "RESOLVED" | "FALSE_ALARM";

export interface AlertRule {
  id: string;
  name: string;
  danger_types: DangerType[];
  min_severity: Severity;
  notification_channels: NotificationChannel[];
  email_recipients: string[];
  is_active: boolean;
  created_at: string;
}

export type NotificationChannel = "WEBSOCKET" | "MQTT" | "EMAIL";
