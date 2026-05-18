import { http } from "@/infrastructure/http/httpClient";
import type { SettingUpdateItem, SettingsGroup } from "../../domain/model/setting";

export const settingApi = {
  getSettings: () => http.get<SettingsGroup>("/api/settings"),
  updateSettings: (updates: SettingUpdateItem[]) =>
    http.patch<SettingsGroup>("/api/settings", { updates }),
};
