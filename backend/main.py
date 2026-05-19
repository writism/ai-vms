from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.domains.alert.adapter.inbound.api.alert_router import router as alert_router
from app.domains.alert.adapter.inbound.api.notification_router import router as notification_router
from app.domains.auth.adapter.inbound.api.auth_router import router as auth_router
from app.domains.camera.adapter.inbound.api.camera_router import router as camera_router
from app.domains.event.adapter.inbound.api.event_router import router as event_router
from app.domains.camera.adapter.inbound.api.network_router import router as network_router
from app.domains.face.adapter.inbound.api.face_router import router as face_router
from app.domains.stream.adapter.inbound.api.stream_router import router as stream_router
from app.domains.agent.adapter.inbound.api.agent_router import router as agent_router
from app.domains.setting.adapter.inbound.api.setting_router import router as setting_router
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

    from app.infrastructure.pipeline.face_recognition_bootstrap import (
        start_face_recognition_pipeline,
        stop_face_recognition_pipeline,
    )
    await start_face_recognition_pipeline()

    try:
        from app.domains.stream.adapter.outbound.external.go2rtc_stream_adapter import Go2RtcStreamAdapter
        from app.infrastructure.stream.camera_stream_sync import sync_cameras_to_streams
        await sync_cameras_to_streams(Go2RtcStreamAdapter())
    except Exception as exc:
        logger.warning("camera→stream sync skipped due to error: %s", exc)

    try:
        if settings.use_database:
            from app.domains.setting.adapter.outbound.persistence.sqlalchemy_setting_repository import (
                SqlAlchemySettingRepository,
            )
            from app.domains.setting.application.usecase.setting_usecase import LoadRuntimeSettingsUseCase
            from app.infrastructure.database.session import async_session_factory

            async with async_session_factory() as session:
                async with session.begin():
                    setting_repo = SqlAlchemySettingRepository(session)
                    await LoadRuntimeSettingsUseCase(setting_repo).execute()
            logger.info("Runtime settings loaded from DB")
    except Exception as exc:
        logger.warning("Runtime settings load skipped: %s", exc)

    try:
        if settings.use_database:
            from app.domains.alert.adapter.outbound.persistence.sqlalchemy_alert_rule_repository import (
                SqlAlchemyAlertRuleRepository,
            )
            from app.domains.alert.domain.entity.alert_rule import AlertRule
            from app.infrastructure.database.session import async_session_factory

            async with async_session_factory() as session:
                async with session.begin():
                    rule_repo = SqlAlchemyAlertRuleRepository(session)
                    existing = await rule_repo.find_all()
                    if not existing:
                        default_rule = AlertRule(
                            name="얼굴 인식 알림",
                            danger_types=["FACE_RECOGNIZED"],
                            min_severity="LOW",
                            notify_websocket=True,
                            notify_mqtt=False,
                            notify_email=False,
                            enable_face_recognition=True,
                            is_active=True,
                        )
                        await rule_repo.save(default_rule)
                        logger.info("Default alert rule created: 얼굴 인식 알림")
    except Exception as exc:
        logger.warning("default alert rule bootstrap skipped: %s", exc)

    yield

    await stop_face_recognition_pipeline()


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

import os
os.makedirs("uploads/faces", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(auth_router, prefix="/api")
app.include_router(camera_router, prefix="/api")
app.include_router(network_router, prefix="/api")
app.include_router(stream_router, prefix="/api")
app.include_router(face_router, prefix="/api")
app.include_router(alert_router, prefix="/api")
app.include_router(event_router, prefix="/api")
app.include_router(notification_router, prefix="/api")
app.include_router(agent_router, prefix="/api")
app.include_router(setting_router, prefix="/api")


@app.get("/health")
async def health_check():
    import asyncio
    import socket

    from app.infrastructure.ai.insightface_service import insightface_service
    from app.infrastructure.ai.yolo_service import yolo_service
    from app.infrastructure.event_bus.mqtt_client import mqtt_client
    from app.infrastructure.pipeline.face_recognition_bootstrap import _engine as _scheduler

    async def check_turn() -> bool:
        try:
            loop = asyncio.get_event_loop()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            await loop.run_in_executor(None, sock.connect, ("coturn", 3478))
            sock.close()
            return True
        except Exception:
            return False

    turn_ok = await check_turn()

    return {
        "status": "ok",
        "service": settings.app_name,
        "version": "0.1.0",
        "services": {
            "insightface": insightface_service.is_loaded,
            "insightface_gpu": insightface_service.use_gpu,
            "yolo": yolo_service.is_loaded,
            "yolo_gpu": yolo_service.use_gpu,
            "turn": turn_ok,
            "mqtt": mqtt_client._connected,
            "face_recognition_pipeline": _scheduler is not None,
        },
    }
