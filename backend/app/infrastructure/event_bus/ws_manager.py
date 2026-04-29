import json
import logging
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketManager:
    def __init__(self) -> None:
        self._connections: list[WebSocket] = []

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self._connections.append(ws)
        logger.info("WebSocket connected, total: %d", len(self._connections))

    def disconnect(self, ws: WebSocket) -> None:
        self._connections.remove(ws)
        logger.info("WebSocket disconnected, total: %d", len(self._connections))

    async def broadcast(self, data: dict) -> None:
        message = json.dumps(data)
        msg_type = data.get("type") if isinstance(data, dict) else None
        active = len(self._connections)
        logger.info("ws broadcast type=%s active=%d", msg_type, active)
        disconnected: list[WebSocket] = []
        sent = 0
        for ws in self._connections:
            try:
                await ws.send_text(message)
                sent += 1
            except Exception as exc:
                logger.warning("ws send failed: %s", exc)
                disconnected.append(ws)
        for ws in disconnected:
            self._connections.remove(ws)
        if active:
            logger.info("ws broadcast sent=%d/%d (dropped=%d)", sent, active, len(disconnected))

    @property
    def connection_count(self) -> int:
        return len(self._connections)


ws_manager = WebSocketManager()
