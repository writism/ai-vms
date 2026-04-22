from pydantic import BaseModel
from uuid import UUID


class DiscoverCamerasRequest(BaseModel):
    timeout: float = 3.0


class BatchRegisterCamerasRequest(BaseModel):
    network_id: UUID | None = None
    cameras: list["CameraRegistrationItem"]


class CameraRegistrationItem(BaseModel):
    name: str
    ip_address: str
    rtsp_url: str | None = None
    onvif_port: int = 80
    manufacturer: str | None = None
    model: str | None = None
