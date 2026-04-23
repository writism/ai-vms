from pydantic import BaseModel
from uuid import UUID


class RegisterCameraRequest(BaseModel):
    name: str
    ip_address: str
    network_id: UUID | None = None
    rtsp_url: str | None = None
    onvif_port: int = 80


class UpdateCameraRequest(BaseModel):
    name: str | None = None
    rtsp_url: str | None = None
    onvif_port: int | None = None
    manufacturer: str | None = None
    model: str | None = None


class FetchRtspUrlRequest(BaseModel):
    username: str
    password: str


class RegisterNetworkRequest(BaseModel):
    name: str
    subnet: str
    description: str | None = None
