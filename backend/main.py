from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.domains.alert.adapter.inbound.api.alert_router import router as alert_router
from app.domains.alert.adapter.inbound.api.notification_router import router as notification_router
from app.domains.auth.adapter.inbound.api.auth_router import router as auth_router
from app.domains.camera.adapter.inbound.api.camera_router import router as camera_router
from app.domains.event.adapter.inbound.api.event_router import router as event_router
from app.domains.camera.adapter.inbound.api.network_router import router as network_router
from app.domains.face.adapter.inbound.api.face_router import router as face_router
from app.domains.stream.adapter.inbound.api.stream_router import router as stream_router
from app.domains.agent.adapter.inbound.api.agent_router import router as agent_router
from app.infrastructure.config.settings import settings
from app.infrastructure.errors import DomainError, domain_error_handler, unhandled_error_handler
from app.infrastructure.logging_config import setup_logging

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    import logging
    logger = logging.getLogger(__name__)

    from app.infrastructure.ai.insightface_service import insightface_service
    from app.infrastructure.ai.yolo_service import yolo_service
    from app.infrastructure.event_bus.mqtt_client import mqtt_client

    await insightface_service.load_models()
    await yolo_service.load_model()
    await mqtt_client.connect()

    from app.domains.auth.adapter.inbound.api.dependencies import _in_memory_user_repo, _password_service
    from app.domains.auth.domain.entity.user import User, UserRole
    existing = await _in_memory_user_repo.find_by_email("admin@ai-vms.io")
    if existing is None:
        admin = User(
            email="admin@ai-vms.io",
            hashed_password=_password_service.hash("admin1234!"),
            name="관리자",
            role=UserRole.ADMIN,
        )
        await _in_memory_user_repo.save(admin)
        logger.info("Default admin user created: admin@ai-vms.io")

    logger.info(
        "AI services: InsightFace=%s, YOLO=%s, MQTT=%s",
        insightface_service.is_loaded,
        yolo_service.is_loaded,
        mqtt_client._connected,
    )

    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_exception_handler(DomainError, domain_error_handler)
app.add_exception_handler(Exception, unhandled_error_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(camera_router, prefix="/api")
app.include_router(network_router, prefix="/api")
app.include_router(stream_router, prefix="/api")
app.include_router(face_router, prefix="/api")
app.include_router(alert_router, prefix="/api")
app.include_router(event_router, prefix="/api")
app.include_router(notification_router, prefix="/api")
app.include_router(agent_router, prefix="/api")


@app.get("/health")
async def health_check():
    import asyncio
    import socket

    from app.infrastructure.ai.insightface_service import insightface_service
    from app.infrastructure.ai.yolo_service import yolo_service
    from app.infrastructure.event_bus.mqtt_client import mqtt_client

    async def check_turn() -> bool:
        try:
            loop = asyncio.get_event_loop()
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(2)
            stun_request = bytes.fromhex("000100002112a442000000000000000000000000")
            await loop.run_in_executor(None, sock.sendto, stun_request, ("localhost", 3478))
            data = await loop.run_in_executor(None, sock.recv, 1024)
            sock.close()
            return len(data) > 0
        except Exception:
            return False

    turn_ok = await check_turn()

    return {
        "status": "ok",
        "service": settings.app_name,
        "version": "0.1.0",
        "services": {
            "insightface": insightface_service.is_loaded,
            "yolo": yolo_service.is_loaded,
            "turn": turn_ok,
            "mqtt": mqtt_client._connected,
        },
    }
