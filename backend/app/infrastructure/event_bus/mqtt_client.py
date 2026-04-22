import json
import logging
from collections.abc import Callable, Coroutine
from typing import Any

from app.infrastructure.config.settings import settings

logger = logging.getLogger(__name__)

MqttHandler = Callable[[str, dict], Coroutine[Any, Any, None]]


class MqttClient:
    def __init__(self) -> None:
        self._client = None
        self._connected = False
        self._handlers: dict[str, list[MqttHandler]] = {}

    async def connect(self) -> bool:
        try:
            import aiomqtt

            url = settings.mqtt_broker_url.replace("mqtt://", "")
            host, _, port_str = url.partition(":")
            port = int(port_str) if port_str else 1883

            self._host = host
            self._port = port
            self._connected = True
            logger.info("MQTT client configured: %s:%d", host, port)
            return True
        except Exception as e:
            logger.warning("MQTT connection setup failed: %s", e)
            self._connected = False
            return False

    async def publish(self, topic: str, data: dict) -> None:
        if not self._connected:
            logger.debug("MQTT not connected, skipping publish to %s", topic)
            return

        full_topic = f"{settings.mqtt_topic_prefix}/{topic}"
        try:
            import aiomqtt

            async with aiomqtt.Client(self._host, self._port) as client:
                await client.publish(full_topic, json.dumps(data).encode())
                logger.debug("MQTT published to %s", full_topic)
        except Exception as e:
            logger.warning("MQTT publish failed: %s", e)

    async def publish_danger_event(self, camera_id: str, danger_type: str, severity: float, description: str | None = None) -> None:
        await self.publish(f"danger/{camera_id}", {
            "type": "DANGER_DETECTED",
            "camera_id": camera_id,
            "danger_type": danger_type,
            "severity": severity,
            "description": description,
        })

    async def publish_face_event(self, camera_id: str, identity_name: str, identity_type: str, confidence: float) -> None:
        await self.publish(f"face/{camera_id}", {
            "type": "FACE_RECOGNIZED",
            "camera_id": camera_id,
            "identity_name": identity_name,
            "identity_type": identity_type,
            "confidence": confidence,
        })

    async def publish_camera_status(self, camera_id: str, status: str) -> None:
        await self.publish(f"camera/{camera_id}/status", {
            "type": "CAMERA_STATUS",
            "camera_id": camera_id,
            "status": status,
        })


mqtt_client = MqttClient()
