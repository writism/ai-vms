from pydantic import BaseModel


class SettingUpdateItem(BaseModel):
    key: str
    value: str


class UpdateSettingsRequest(BaseModel):
    updates: list[SettingUpdateItem]
