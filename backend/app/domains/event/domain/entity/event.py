from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


class EventType(StrEnum):
    FACE_RECOGNIZED = "FACE_RECOGNIZED"
    FACE_UNIDENTIFIED = "FACE_UNIDENTIFIED"
    DANGER_DETECTED = "DANGER_DETECTED"
    CAMERA_ONLINE = "CAMERA_ONLINE"
    CAMERA_OFFLINE = "CAMERA_OFFLINE"
    ACCESS_GRANTED = "ACCESS_GRANTED"
    ACCESS_DENIED = "ACCESS_DENIED"


@dataclass
class Event:
    event_type: EventType
    camera_id: UUID | None = None
    identity_id: UUID | None = None
    danger_event_id: UUID | None = None
    description: str | None = None
    metadata: dict | None = None
    snapshot_path: str | None = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
