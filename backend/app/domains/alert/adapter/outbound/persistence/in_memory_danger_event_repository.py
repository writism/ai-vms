from uuid import UUID

from app.domains.alert.application.port.danger_event_repository_port import DangerEventRepositoryPort
from app.domains.alert.domain.entity.danger_event import DangerEvent


class InMemoryDangerEventRepository(DangerEventRepositoryPort):
    def __init__(self) -> None:
        self._store: dict[UUID, DangerEvent] = {}

    async def save(self, event: DangerEvent) -> DangerEvent:
        self._store[event.id] = event
        return event

    async def find_by_id(self, event_id: UUID) -> DangerEvent | None:
        return self._store.get(event_id)

    async def find_all(
        self,
        danger_type: str | None = None,
        severity: str | None = None,
        status: str | None = None,
        camera_id: UUID | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[DangerEvent]:
        result = list(self._store.values())
        if danger_type:
            result = [e for e in result if e.danger_type.value == danger_type]
        if severity:
            result = [e for e in result if e.severity.value == severity]
        if status:
            result = [e for e in result if e.status.value == status]
        if camera_id:
            result = [e for e in result if e.camera_id == camera_id]
        result.sort(key=lambda e: e.created_at, reverse=True)
        return result[offset : offset + limit]

    async def count(
        self,
        danger_type: str | None = None,
        severity: str | None = None,
        status: str | None = None,
    ) -> int:
        result = list(self._store.values())
        if danger_type:
            result = [e for e in result if e.danger_type.value == danger_type]
        if severity:
            result = [e for e in result if e.severity.value == severity]
        if status:
            result = [e for e in result if e.status.value == status]
        return len(result)
