import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.infrastructure.event_bus.ws_manager import ws_manager

logger = logging.getLogger(__name__)

router = APIRouter(tags=["notification"])


@router.websocket("/ws/notifications")
async def notifications_ws(ws: WebSocket):
    await ws_manager.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(ws)
