from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.domains.event.domain.entity.event import Event, EventType


class EventResponse(BaseModel):
    id: UUID
    event_type: EventType
    camera_id: UUID | None
    identity_id: UUID | None
    danger_event_id: UUID | None
    description: str | None
    metadata: dict | None
    snapshot_path: str | None
    created_at: datetime

    @staticmethod
    def from_entity(e: Event) -> "EventResponse":
        return EventResponse(
            id=e.id,
            event_type=e.event_type,
            camera_id=e.camera_id,
            identity_id=e.identity_id,
            danger_event_id=e.danger_event_id,
            description=e.description,
            metadata=e.metadata,
            snapshot_path=e.snapshot_path,
            created_at=e.created_at,
        )


class EventListResponse(BaseModel):
    items: list[EventResponse]
    total: int
