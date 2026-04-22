from datetime import datetime
from uuid import UUID

from app.domains.event.application.port.event_repository_port import EventRepositoryPort
from app.domains.event.domain.entity.event import Event


class InMemoryEventRepository(EventRepositoryPort):
    def __init__(self) -> None:
        self._store: dict[UUID, Event] = {}

    async def save(self, event: Event) -> Event:
        self._store[event.id] = event
        return event

    async def find_by_id(self, event_id: UUID) -> Event | None:
        return self._store.get(event_id)

    async def find_all(
        self,
        event_type: str | None = None,
        camera_id: UUID | None = None,
        identity_id: UUID | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Event]:
        result = list(self._store.values())
        if event_type:
            result = [e for e in result if e.event_type.value == event_type]
        if camera_id:
            result = [e for e in result if e.camera_id == camera_id]
        if identity_id:
            result = [e for e in result if e.identity_id == identity_id]
        if from_date:
            result = [e for e in result if e.created_at >= from_date]
        if to_date:
            result = [e for e in result if e.created_at <= to_date]
        result.sort(key=lambda e: e.created_at, reverse=True)
        return result[offset : offset + limit]

    async def count(
        self,
        event_type: str | None = None,
        camera_id: UUID | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> int:
        result = list(self._store.values())
        if event_type:
            result = [e for e in result if e.event_type.value == event_type]
        if camera_id:
            result = [e for e in result if e.camera_id == camera_id]
        if from_date:
            result = [e for e in result if e.created_at >= from_date]
        if to_date:
            result = [e for e in result if e.created_at <= to_date]
        return len(result)
