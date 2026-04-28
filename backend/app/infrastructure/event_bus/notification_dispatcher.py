import logging

from app.domains.alert.domain.entity.alert_rule import AlertRule
from app.domains.alert.domain.entity.danger_event import DangerEvent
from app.infrastructure.event_bus.mqtt_client import mqtt_client
from app.infrastructure.event_bus.ws_manager import ws_manager

logger = logging.getLogger(__name__)


class NotificationDispatcher:
    async def dispatch(self, event: DangerEvent, rules: list[AlertRule]) -> int:
        dispatched = 0

        for rule in rules:
            if not rule.is_active:
                continue
            if event.danger_type.value not in rule.danger_types:
                continue

            severity_order = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
            event_idx = severity_order.index(event.severity.value)
            rule_idx = severity_order.index(rule.min_severity)
            if event_idx < rule_idx:
                continue

            if rule.notify_websocket:
                await ws_manager.broadcast({
                    "type": "DANGER_EVENT",
                    "data": {
                        "event_id": str(event.id),
                        "danger_type": event.danger_type.value,
                        "severity": event.severity.value,
                        "camera_id": str(event.camera_id),
                        "description": event.description,
                    },
                })
                dispatched += 1

            if rule.notify_mqtt:
                await mqtt_client.publish_danger_event(
                    camera_id=str(event.camera_id),
                    danger_type=event.danger_type.value,
                    severity=float(severity_order.index(event.severity.value)) / 3.0,
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
