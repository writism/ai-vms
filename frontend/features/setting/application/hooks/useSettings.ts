"use client";

import { useState } from "react";
import useSWR from "swr";
import type { SettingItem, SettingUpdateItem, SettingsGroup } from "../../domain/model/setting";
import { settingApi } from "../../infrastructure/api/settingApi";

export function useSettings() {
  const { data, error, isLoading, mutate } = useSWR<SettingsGroup>("/api/settings");
  const [saving, setSaving] = useState(false);

  const updateSettings = async (updates: SettingUpdateItem[]) => {
    setSaving(true);
    try {
      const updated = await settingApi.updateSettings(updates);
      await mutate(updated, false);
    } finally {
      setSaving(false);
    }
  };

  return {
    settings: data,
    isLoading,
    error,
    saving,
    updateSettings,
  };
}

export function formatValue(item: SettingItem): string {
  return item.value;
}

export function parseValue(item: SettingItem, raw: string): string {
  if (item.type === "bool") {
    return raw === "true" ? "true" : "false";
  }
  return raw;
}
