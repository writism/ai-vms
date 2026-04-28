from pydantic import BaseModel, field_validator
from uuid import UUID


def _validate_rtsp_url(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    if stripped == "":
        return None
    if not (stripped.startswith("rtsp://") or stripped.startswith("rtsps://")):
        raise ValueError("RTSP URL은 'rtsp://' 또는 'rtsps://'로 시작해야 합니다")
    return stripped


class RegisterCameraRequest(BaseModel):
    name: str
    ip_address: str
    network_id: UUID | None = None
    rtsp_url: str | None = None
    onvif_port: int = 80

    @field_validator("rtsp_url")
    @classmethod
    def _check_rtsp_url(cls, v: str | None) -> str | None:
        return _validate_rtsp_url(v)


class UpdateCameraRequest(BaseModel):
    name: str | None = None
    rtsp_url: str | None = None
    onvif_port: int | None = None
    manufacturer: str | None = None
    model: str | None = None

    @field_validator("rtsp_url")
    @classmethod
    def _check_rtsp_url(cls, v: str | None) -> str | None:
        return _validate_rtsp_url(v)


class FetchRtspUrlRequest(BaseModel):
    username: str
    password: str


class RegisterNetworkRequest(BaseModel):
    name: str
    subnet: str
    description: str | None = None
