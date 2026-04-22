from uuid import UUID

from app.domains.alert.application.port.alert_rule_repository_port import AlertRuleRepositoryPort
from app.domains.alert.domain.entity.alert_rule import AlertRule


class InMemoryAlertRuleRepository(AlertRuleRepositoryPort):
    def __init__(self) -> None:
        self._store: dict[UUID, AlertRule] = {}

    async def save(self, rule: AlertRule) -> AlertRule:
        self._store[rule.id] = rule
        return rule

    async def find_by_id(self, rule_id: UUID) -> AlertRule | None:
        return self._store.get(rule_id)

    async def find_all(self) -> list[AlertRule]:
        return list(self._store.values())

    async def find_active_rules(self) -> list[AlertRule]:
        return [r for r in self._store.values() if r.is_active]

    async def delete(self, rule_id: UUID) -> bool:
        return self._store.pop(rule_id, None) is not None
