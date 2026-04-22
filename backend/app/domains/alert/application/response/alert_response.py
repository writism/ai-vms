from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.domains.alert.domain.entity.alert_rule import AlertRule
from app.domains.alert.domain.entity.danger_event import DangerEvent, DangerType, EventStatus, Severity


class DangerEventResponse(BaseModel):
    id: UUID
    camera_id: UUID
    danger_type: DangerType
    severity: Severity
    confidence: float
    description: str | None
    snapshot_path: str | None
    status: EventStatus
    resolved_by: UUID | None
    resolved_at: datetime | None
    created_at: datetime

    @staticmethod
    def from_entity(e: DangerEvent) -> "DangerEventResponse":
        return DangerEventResponse(
            id=e.id,
            camera_id=e.camera_id,
            danger_type=e.danger_type,
            severity=e.severity,
            confidence=e.confidence,
            description=e.description,
            snapshot_path=e.snapshot_path,
            status=e.status,
            resolved_by=e.resolved_by,
            resolved_at=e.resolved_at,
            created_at=e.created_at,
        )


class DangerEventListResponse(BaseModel):
    items: list[DangerEventResponse]
    total: int


class AlertRuleResponse(BaseModel):
    id: UUID
    name: str
    danger_types: list[str]
    min_severity: str
    notify_websocket: bool
    notify_mqtt: bool
    notify_email: bool
    email_recipients: list[str]
    is_active: bool
    created_at: datetime

    @staticmethod
    def from_entity(r: AlertRule) -> "AlertRuleResponse":
        return AlertRuleResponse(
            id=r.id,
            name=r.name,
            danger_types=r.danger_types,
            min_severity=r.min_severity,
            notify_websocket=r.notify_websocket,
            notify_mqtt=r.notify_mqtt,
            notify_email=r.notify_email,
            email_recipients=r.email_recipients,
            is_active=r.is_active,
            created_at=r.created_at,
        )
