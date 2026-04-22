from uuid import UUID

from app.domains.alert.application.port.alert_rule_repository_port import AlertRuleRepositoryPort
from app.domains.alert.application.request.alert_request import CreateAlertRuleRequest
from app.domains.alert.application.response.alert_response import AlertRuleResponse
from app.domains.alert.domain.entity.alert_rule import AlertRule


class CreateAlertRuleUseCase:
    def __init__(self, repo: AlertRuleRepositoryPort):
        self._repo = repo

    async def execute(self, request: CreateAlertRuleRequest) -> AlertRuleResponse:
        rule = AlertRule(
            name=request.name,
            danger_types=request.danger_types,
            min_severity=request.min_severity,
            notify_websocket=request.notify_websocket,
            notify_mqtt=request.notify_mqtt,
            notify_email=request.notify_email,
            email_recipients=request.email_recipients,
        )
        saved = await self._repo.save(rule)
        return AlertRuleResponse.from_entity(saved)


class ListAlertRulesUseCase:
    def __init__(self, repo: AlertRuleRepositoryPort):
        self._repo = repo

    async def execute(self) -> list[AlertRuleResponse]:
        rules = await self._repo.find_all()
        return [AlertRuleResponse.from_entity(r) for r in rules]


class DeleteAlertRuleUseCase:
    def __init__(self, repo: AlertRuleRepositoryPort):
        self._repo = repo

    async def execute(self, rule_id: UUID) -> bool:
        return await self._repo.delete(rule_id)
