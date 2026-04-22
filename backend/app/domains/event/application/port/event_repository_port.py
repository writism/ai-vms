from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.domains.event.domain.entity.event import Event


class EventRepositoryPort(ABC):
    @abstractmethod
    async def save(self, event: Event) -> Event: ...

    @abstractmethod
    async def find_by_id(self, event_id: UUID) -> Event | None: ...

    @abstractmethod
    async def find_all(
        self,
        event_type: str | None = None,
        camera_id: UUID | None = None,
        identity_id: UUID | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Event]: ...

    @abstractmethod
    async def count(
        self,
        event_type: str | None = None,
        camera_id: UUID | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> int: ...
