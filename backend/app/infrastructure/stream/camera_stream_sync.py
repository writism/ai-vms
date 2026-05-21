import logging
import re

from app.domains.stream.application.port.stream_port import StreamPort

logger = logging.getLogger(__name__)

UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


def is_camera_stream_name(name: str) -> bool:
    return bool(UUID_RE.match(name))


async def sync_cameras_to_streams(stream_port: StreamPort) -> tuple[int, int]:
    from app.domains.camera.adapter.outbound.persistence.sqlalchemy_camera_repository import (
        SqlAlchemyCameraRepository,
    )
    from app.infrastructure.config.settings import settings
    from app.infrastructure.database.session import async_session_factory

    if not settings.use_database:
        logger.info("camera→stream sync skipped: USE_DATABASE=false")
        return (0, 0)

    async with async_session_factory() as session:
        repo = SqlAlchemyCameraRepository(session)
        cameras = await repo.find_all()

    camera_ids = {str(cam.id) for cam in cameras}

    # Remove orphaned streams (UUID-named streams not in DB)
    try:
        existing = await stream_port.list_streams()
        for name in list(existing.keys()):
            if is_camera_stream_name(name) and name not in camera_ids:
                try:
                    await stream_port.unregister_stream(name)
                    logger.info("removed orphaned go2rtc stream: %s", name)
                except Exception as exc:
                    logger.warning("failed to remove orphaned stream %s: %s", name, exc)
    except Exception as exc:
        logger.warning("could not list go2rtc streams for cleanup: %s", exc)

    registered = 0
    failed = 0
    for cam in cameras:
        if not cam.rtsp_url:
            continue
        try:
            ok = await stream_port.register_stream(str(cam.id), cam.rtsp_url)
            if ok:
                registered += 1
            else:
                failed += 1
                logger.warning("go2rtc rejected camera stream %s", cam.id)
        except Exception as exc:
            failed += 1
            logger.warning("go2rtc sync failed for %s: %s", cam.id, exc)

    logger.info(
        "camera→stream sync complete: cameras=%d registered=%d failed=%d",
        len(cameras),
        registered,
        failed,
    )
    return (registered, failed)
