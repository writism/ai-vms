from app.domains.alert.adapter.outbound.persistence.in_memory_alert_rule_repository import InMemoryAlertRuleRepository
from app.domains.alert.adapter.outbound.persistence.in_memory_danger_event_repository import InMemoryDangerEventRepository
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

_event_repo = InMemoryDangerEventRepository()
_rule_repo = InMemoryAlertRuleRepository()


def get_create_danger_event_usecase() -> CreateDangerEventUseCase:
    return CreateDangerEventUseCase(_event_repo)


def get_list_danger_events_usecase() -> ListDangerEventsUseCase:
    return ListDangerEventsUseCase(_event_repo)


def get_update_event_status_usecase() -> UpdateEventStatusUseCase:
    return UpdateEventStatusUseCase(_event_repo)


def get_create_alert_rule_usecase() -> CreateAlertRuleUseCase:
    return CreateAlertRuleUseCase(_rule_repo)


def get_list_alert_rules_usecase() -> ListAlertRulesUseCase:
    return ListAlertRulesUseCase(_rule_repo)


def get_delete_alert_rule_usecase() -> DeleteAlertRuleUseCase:
    return DeleteAlertRuleUseCase(_rule_repo)
