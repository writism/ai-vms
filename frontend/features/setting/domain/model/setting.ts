export interface SettingItem {
  key: string;
  value: string;
  type: "float" | "int" | "bool" | "string";
  label: string;
}

export interface SettingsGroup {
  recognition: SettingItem[];
  clustering: SettingItem[];
  pipeline: SettingItem[];
}

export interface SettingUpdateItem {
  key: string;
  value: string;
}
