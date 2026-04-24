from urllib.parse import urlparse

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.stream.adapter.outbound.external.go2rtc_stream_adapter import Go2RtcStreamAdapter
from app.domains.stream.application.usecase.stream_usecase import (
    ListStreamsUseCase,
    RegisterStreamUseCase,
    ScanMediaServersUseCase,
    UnregisterStreamUseCase,
    WebRTCOfferUseCase,
)
from app.infrastructure.config.settings import settings

_stream_adapter = Go2RtcStreamAdapter()


def get_register_stream_usecase() -> RegisterStreamUseCase:
    return RegisterStreamUseCase(_stream_adapter)


def get_unregister_stream_usecase() -> UnregisterStreamUseCase:
    return UnregisterStreamUseCase(_stream_adapter)


def get_list_streams_usecase() -> ListStreamsUseCase:
    return ListStreamsUseCase(_stream_adapter)


def get_webrtc_offer_usecase() -> WebRTCOfferUseCase:
    return WebRTCOfferUseCase(_stream_adapter)


def _get_own_server_ip() -> str | None:
    try:
        parsed = urlparse(settings.go2rtc_url)
        host = parsed.hostname
        if host and host not in ("localhost", "127.0.0.1", "0.0.0.0"):
            return host
    except Exception:
        pass
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None


async def _get_session_optional():
    if settings.use_database:
        from app.infrastructure.database.session import get_async_session
        async for session in get_async_session():
            yield session
    else:
        yield None


async def get_scan_media_servers_usecase(
    session: AsyncSession | None = Depends(_get_session_optional),
) -> ScanMediaServersUseCase:
    from app.domains.camera.adapter.inbound.api.dependencies import _get_camera_repo

    repo = _get_camera_repo(session)
    cameras = await repo.find_all()
    camera_ips = {c.ip_address for c in cameras}
    own_ip = _get_own_server_ip()
    return ScanMediaServersUseCase(registered_camera_ips=camera_ips, own_server_ip=own_ip)
