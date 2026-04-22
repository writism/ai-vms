from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.domains.camera.domain.entity.camera import Camera, CameraStatus
from app.domains.camera.domain.entity.network import Network


class CameraResponse(BaseModel):
    id: UUID
    name: str
    ip_address: str
    network_id: UUID | None
    status: CameraStatus
    rtsp_url: str | None
    onvif_port: int
    manufacturer: str | None
    model: str | None
    created_at: datetime

    @staticmethod
    def from_entity(entity: Camera) -> "CameraResponse":
        return CameraResponse(
            id=entity.id,
            name=entity.name,
            ip_address=entity.ip_address,
            network_id=entity.network_id,
            status=entity.status,
            rtsp_url=entity.rtsp_url,
            onvif_port=entity.onvif_port,
            manufacturer=entity.manufacturer,
            model=entity.model,
            created_at=entity.created_at,
        )


class NetworkResponse(BaseModel):
    id: UUID
    name: str
    subnet: str
    description: str | None
    is_active: bool
    created_at: datetime

    @staticmethod
    def from_entity(entity: Network) -> "NetworkResponse":
        return NetworkResponse(
            id=entity.id,
            name=entity.name,
            subnet=entity.subnet,
            description=entity.description,
            is_active=entity.is_active,
            created_at=entity.created_at,
        )
