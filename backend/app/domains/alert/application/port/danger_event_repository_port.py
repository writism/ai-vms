from abc import ABC, abstractmethod
from uuid import UUID

from app.domains.alert.domain.entity.danger_event import DangerEvent


class DangerEventRepositoryPort(ABC):
    @abstractmethod
    async def save(self, event: DangerEvent) -> DangerEvent: ...

    @abstractmethod
    async def find_by_id(self, event_id: UUID) -> DangerEvent | None: ...

    @abstractmethod
    async def find_all(
        self,
        danger_type: str | None = None,
        severity: str | None = None,
        status: str | None = None,
        camera_id: UUID | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[DangerEvent]: ...

    @abstractmethod
    async def count(
        self,
        danger_type: str | None = None,
        severity: str | None = None,
        status: str | None = None,
        camera_id: UUID | None = None,
    ) -> int: ...
