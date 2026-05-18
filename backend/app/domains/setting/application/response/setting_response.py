from pydantic import BaseModel


class SettingItemResponse(BaseModel):
    key: str
    value: str
    type: str
    label: str


class SettingsGroupResponse(BaseModel):
    recognition: list[SettingItemResponse]
    clustering: list[SettingItemResponse]
    pipeline: list[SettingItemResponse]
