import logging

from app.domains.alert.application.response.alert_response import DangerEventResponse
from app.domains.alert.domain.entity.alert_rule import AlertRule
from app.domains.alert.domain.entity.danger_event import DangerEvent, DangerType
from app.infrastructure.event_bus.mqtt_client import mqtt_client
from app.infrastructure.event_bus.ws_manager import ws_manager

logger = logging.getLogger(__name__)

_SEVERITY_ORDER = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]


def _rule_matches(event: DangerEvent, rule: AlertRule) -> bool:
    if not rule.is_active:
        return False
    if event.danger_type == DangerType.FACE_RECOGNIZED:
        if not rule.enable_face_recognition:
            return False
    elif event.danger_type.value not in rule.danger_types:
        return False
    try:
        if _SEVERITY_ORDER.index(event.severity.value) < _SEVERITY_ORDER.index(rule.min_severity):
            return False
    except ValueError:
        return False
    return True


class NotificationDispatcher:
    async def dispatch(self, event: DangerEvent, rules: list[AlertRule]) -> int:
        dispatched = 0

        for rule in rules:
            if not _rule_matches(event, rule):
                continue

            if rule.notify_websocket:
                await ws_manager.broadcast({
                    "type": "DANGER_EVENT",
                    "data": DangerEventResponse.from_entity(event).model_dump(mode="json"),
                })
                dispatched += 1

            if rule.notify_mqtt:
                await mqtt_client.publish_danger_event(
                    camera_id=str(event.camera_id),
                    danger_type=event.danger_type.value,
                    severity=float(_SEVERITY_ORDER.index(event.severity.value)) / 3.0,
                    description=event.description,
                )
                dispatched += 1

            if rule.notify_email and rule.email_recipients:
                logger.info(
                    "Email notification to %s for event %s (not implemented)",
                    rule.email_recipients,
                    event.id,
                )
                dispatched += 1

        return dispatched


notification_dispatcher = NotificationDispatcher()
