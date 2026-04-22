export interface Notification {
  id: string;
  type: string;
  data: Record<string, unknown>;
  timestamp: number;
  read: boolean;
}

export type NotificationChannel = "WEBSOCKET" | "MQTT" | "EMAIL";
