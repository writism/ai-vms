from abc import ABC, abstractmethod
from uuid import UUID

from app.domains.alert.domain.entity.alert_rule import AlertRule


class AlertRuleRepositoryPort(ABC):
    @abstractmethod
    async def save(self, rule: AlertRule) -> AlertRule: ...

    @abstractmethod
    async def find_by_id(self, rule_id: UUID) -> AlertRule | None: ...

    @abstractmethod
    async def find_all(self) -> list[AlertRule]: ...

    @abstractmethod
    async def find_active_rules(self) -> list[AlertRule]: ...

    @abstractmethod
    async def delete(self, rule_id: UUID) -> bool: ...
