from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


class CameraStatus(StrEnum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    ERROR = "ERROR"


@dataclass
class Camera:
    name: str
    ip_address: str
    network_id: UUID | None = None
    status: CameraStatus = CameraStatus.OFFLINE
    rtsp_url: str | None = None
    onvif_port: int = 80
    manufacturer: str | None = None
    model: str | None = None
    firmware_version: str | None = None
    mac_address: str | None = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
