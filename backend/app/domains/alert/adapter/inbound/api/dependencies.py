from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.alert.adapter.outbound.persistence.in_memory_alert_rule_repository import InMemoryAlertRuleRepository
from app.domains.alert.adapter.outbound.persistence.in_memory_danger_event_repository import InMemoryDangerEventRepository
from app.domains.alert.application.port.alert_rule_repository_port import AlertRuleRepositoryPort
from app.domains.alert.application.port.danger_event_repository_port import DangerEventRepositoryPort
from app.domains.alert.application.usecase.alert_rule_usecase import (
    CreateAlertRuleUseCase,
    DeleteAlertRuleUseCase,
    ListAlertRulesUseCase,
)
from app.domains.alert.application.usecase.danger_event_usecase import (
    CreateDangerEventUseCase,
    ListDangerEventsUseCase,
    UpdateEventStatusUseCase,
)
from app.infrastructure.config.settings import settings

_in_memory_event_repo = InMemoryDangerEventRepository()
_in_memory_rule_repo = InMemoryAlertRuleRepository()


def _get_event_repo(session: AsyncSession | None = None) -> DangerEventRepositoryPort:
    if settings.use_database and session:
        from app.domains.alert.adapter.outbound.persistence.sqlalchemy_danger_event_repository import SqlAlchemyDangerEventRepository
        return SqlAlchemyDangerEventRepository(session)
    return _in_memory_event_repo


def _get_rule_repo(session: AsyncSession | None = None) -> AlertRuleRepositoryPort:
    if settings.use_database and session:
        from app.domains.alert.adapter.outbound.persistence.sqlalchemy_alert_rule_repository import SqlAlchemyAlertRuleRepository
        return SqlAlchemyAlertRuleRepository(session)
    return _in_memory_rule_repo


def get_create_danger_event_usecase() -> CreateDangerEventUseCase:
    return CreateDangerEventUseCase(_get_event_repo())


def get_list_danger_events_usecase() -> ListDangerEventsUseCase:
    return ListDangerEventsUseCase(_get_event_repo())


def get_update_event_status_usecase() -> UpdateEventStatusUseCase:
    return UpdateEventStatusUseCase(_get_event_repo())


def get_create_alert_rule_usecase() -> CreateAlertRuleUseCase:
    return CreateAlertRuleUseCase(_get_rule_repo())


def get_list_alert_rules_usecase() -> ListAlertRulesUseCase:
    return ListAlertRulesUseCase(_get_rule_repo())


def get_delete_alert_rule_usecase() -> DeleteAlertRuleUseCase:
    return DeleteAlertRuleUseCase(_get_rule_repo())
