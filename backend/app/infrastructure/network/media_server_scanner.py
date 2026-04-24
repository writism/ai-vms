import asyncio
import logging
import re
from dataclasses import dataclass, field
from ipaddress import IPv4Network
from urllib.parse import urlparse

import httpx

logger = logging.getLogger(__name__)

GO2RTC_API_PORT = 1984
SCAN_TIMEOUT = 1.5
API_TIMEOUT = 3.0


@dataclass
class MediaServerStream:
    name: str
    url: str
    camera_ip: str | None = None


@dataclass
class MediaServerInfo:
    ip: str
    port: int = GO2RTC_API_PORT
    reachable: bool = False
    streams: list[MediaServerStream] = field(default_factory=list)
    is_own: bool = False


@dataclass
class CameraConflict:
    camera_ip: str
    servers: list[str]


def _extract_camera_ip(rtsp_url: str) -> str | None:
    try:
        parsed = urlparse(rtsp_url)
        return parsed.hostname
    except Exception:
        return None


def _mask_url(rtsp_url: str) -> str:
    if not rtsp_url:
        return rtsp_url
    try:
        parsed = urlparse(rtsp_url)
        if parsed.password:
            masked = parsed._replace(
                netloc=f"{parsed.username}:****@{parsed.hostname}"
                + (f":{parsed.port}" if parsed.port else "")
            )
            return masked.geturl()
    except Exception:
        pass
    return rtsp_url


async def _check_port(ip: str, port: int, timeout: float) -> bool:
    try:
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(ip, port),
            timeout=timeout,
        )
        writer.close()
        await writer.wait_closed()
        return True
    except (OSError, asyncio.TimeoutError):
        return False


async def _query_streams(ip: str, port: int) -> list[MediaServerStream]:
    url = f"http://{ip}:{port}/api/streams"
    try:
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
        streams = []
        for name, info in data.items():
            producers = info if isinstance(info, list) else info.get("producers", [])
            src_url = ""
            if isinstance(producers, list) and producers:
                first = producers[0]
                src_url = first if isinstance(first, str) else first.get("url", "")
            camera_ip = _extract_camera_ip(src_url) if src_url else None
            streams.append(MediaServerStream(name=name, url=_mask_url(src_url), camera_ip=camera_ip))
        return streams
    except Exception as e:
        logger.debug("Failed to query streams from %s:%d — %s", ip, port, e)
        return []


async def scan_media_servers(
    subnet: str,
    own_server_ip: str | None = None,
    port: int = GO2RTC_API_PORT,
) -> list[MediaServerInfo]:
    try:
        network = IPv4Network(subnet, strict=False)
    except ValueError:
        logger.error("Invalid subnet: %s", subnet)
        return []

    hosts = [str(h) for h in network.hosts()]
    if len(hosts) > 1022:
        hosts = hosts[:1022]

    semaphore = asyncio.Semaphore(100)

    async def probe(ip: str) -> MediaServerInfo | None:
        async with semaphore:
            if not await _check_port(ip, port, SCAN_TIMEOUT):
                return None
            streams = await _query_streams(ip, port)
            is_own = own_server_ip is not None and ip == own_server_ip
            return MediaServerInfo(
                ip=ip, port=port, reachable=True,
                streams=streams, is_own=is_own,
            )

    results = await asyncio.gather(*(probe(ip) for ip in hosts))
    return [r for r in results if r is not None]


def detect_conflicts(
    servers: list[MediaServerInfo],
    registered_camera_ips: set[str],
) -> list[CameraConflict]:
    camera_to_servers: dict[str, list[str]] = {}
    for server in servers:
        for stream in server.streams:
            if stream.camera_ip and stream.camera_ip in registered_camera_ips:
                camera_to_servers.setdefault(stream.camera_ip, []).append(server.ip)
    return [
        CameraConflict(camera_ip=ip, servers=srvs)
        for ip, srvs in camera_to_servers.items()
        if len(srvs) > 1
    ]
