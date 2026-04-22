"use client";

import useSWR from "swr";

export interface AlertRule {
  id: string;
  name: string;
  danger_types: string[];
  min_severity: string;
  notify_websocket: boolean;
  notify_mqtt: boolean;
  notify_email: boolean;
  email_recipients: string[];
  is_active: boolean;
  created_at: string;
}

export function useAlertRules() {
  const { data, error, isLoading, mutate } = useSWR<AlertRule[]>("/api/alerts/rules");

  return {
    rules: data ?? [],
    isLoading,
    error,
    refresh: mutate,
  };
}
