from app.domains.alert.domain.entity.alert_rule import AlertRule
from app.domains.alert.domain.entity.danger_event import (
    DangerEvent,
    DangerType,
    EventStatus,
    Severity,
)
from app.domains.alert.infrastructure.orm.alert_orm import AlertRuleORM, DangerEventORM


class DangerEventMapper:
    @staticmethod
    def to_entity(orm: DangerEventORM) -> DangerEvent:
        return DangerEvent(
            id=orm.id,
            camera_id=orm.camera_id,
            danger_type=DangerType(orm.danger_type),
            severity=Severity(orm.severity),
            confidence=orm.confidence,
            description=orm.description,
            snapshot_path=orm.snapshot_path,
            status=EventStatus(orm.status),
            resolved_by=orm.resolved_by,
            resolved_at=orm.resolved_at,
            created_at=orm.created_at,
        )

    @staticmethod
    def to_orm(entity: DangerEvent) -> DangerEventORM:
        return DangerEventORM(
            id=entity.id,
            camera_id=entity.camera_id,
            danger_type=entity.danger_type.value,
            severity=entity.severity.value,
            confidence=entity.confidence,
            description=entity.description,
            snapshot_path=entity.snapshot_path,
            status=entity.status.value,
            resolved_by=entity.resolved_by,
            resolved_at=entity.resolved_at,
            created_at=entity.created_at,
        )


class AlertRuleMapper:
    @staticmethod
    def to_entity(orm: AlertRuleORM) -> AlertRule:
        return AlertRule(
            id=orm.id,
            name=orm.name,
            danger_types=list(orm.danger_types),
            min_severity=orm.min_severity,
            notify_websocket=orm.notify_websocket,
            notify_mqtt=orm.notify_mqtt,
            notify_email=orm.notify_email,
            email_recipients=list(orm.email_recipients),
            is_active=orm.is_active,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    @staticmethod
    def to_orm(entity: AlertRule) -> AlertRuleORM:
        return AlertRuleORM(
            id=entity.id,
            name=entity.name,
            danger_types=entity.danger_types,
            min_severity=entity.min_severity,
            notify_websocket=entity.notify_websocket,
            notify_mqtt=entity.notify_mqtt,
            notify_email=entity.notify_email,
            email_recipients=entity.email_recipients,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
