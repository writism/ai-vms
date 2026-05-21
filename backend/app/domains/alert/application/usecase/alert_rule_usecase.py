from uuid import UUID

from app.domains.alert.application.port.alert_rule_repository_port import AlertRuleRepositoryPort
from app.domains.alert.application.request.alert_request import CreateAlertRuleRequest, UpdateAlertRuleRequest
from app.domains.alert.application.response.alert_response import AlertRuleResponse
from app.domains.alert.domain.entity.alert_rule import AlertRule


class CreateAlertRuleUseCase:
    def __init__(self, repo: AlertRuleRepositoryPort):
        self._repo = repo

    async def execute(self, request: CreateAlertRuleRequest) -> AlertRuleResponse:
        rule = AlertRule(
            name=request.name,
            camera_id=request.camera_id,
            danger_types=request.danger_types,
            min_severity=request.min_severity,
            notify_websocket=request.notify_websocket,
            notify_mqtt=request.notify_mqtt,
            notify_email=request.notify_email,
            email_recipients=request.email_recipients,
            enable_face_recognition=request.enable_face_recognition,
        )
        saved = await self._repo.save(rule)
        return AlertRuleResponse.from_entity(saved)


class UpdateAlertRuleUseCase:
    def __init__(self, repo: AlertRuleRepositoryPort):
        self._repo = repo

    async def execute(self, rule_id: UUID, request: UpdateAlertRuleRequest) -> AlertRuleResponse | None:
        rule = await self._repo.find_by_id(rule_id)
        if rule is None:
            return None
        if request.name is not None:
            rule.name = request.name
        if request.camera_id is not None or "camera_id" in request.model_fields_set:
            rule.camera_id = request.camera_id
        if request.danger_types is not None:
            rule.danger_types = request.danger_types
        if request.min_severity is not None:
            rule.min_severity = request.min_severity
        if request.notify_websocket is not None:
            rule.notify_websocket = request.notify_websocket
        if request.notify_mqtt is not None:
            rule.notify_mqtt = request.notify_mqtt
        if request.notify_email is not None:
            rule.notify_email = request.notify_email
        if request.email_recipients is not None:
            rule.email_recipients = request.email_recipients
        if request.enable_face_recognition is not None:
            rule.enable_face_recognition = request.enable_face_recognition
        if request.is_active is not None:
            rule.is_active = request.is_active
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
