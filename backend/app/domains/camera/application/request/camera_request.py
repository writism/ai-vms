from pydantic import BaseModel
from uuid import UUID


class RegisterCameraRequest(BaseModel):
    name: str
    ip_address: str
    network_id: UUID | None = None
    rtsp_url: str | None = None
    onvif_port: int = 80


class RegisterNetworkRequest(BaseModel):
    name: str
    subnet: str
    description: str | None = None
