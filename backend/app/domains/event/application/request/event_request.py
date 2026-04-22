from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CreateEventRequest(BaseModel):
    event_type: str
    camera_id: UUID | None = None
    identity_id: UUID | None = None
    danger_event_id: UUID | None = None
    description: str | None = None
    metadata: dict | None = None
    snapshot_path: str | None = None


class ListEventsRequest(BaseModel):
    event_type: str | None = None
    camera_id: UUID | None = None
    identity_id: UUID | None = None
    from_date: datetime | None = None
    to_date: datetime | None = None
    limit: int = 50
    offset: int = 0
