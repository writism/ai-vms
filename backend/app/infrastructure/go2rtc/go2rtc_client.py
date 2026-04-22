import logging
from dataclasses import dataclass

import httpx

from app.infrastructure.config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class Go2RtcStream:
    name: str
    producers: list[dict]


class Go2RtcClient:
    def __init__(self, base_url: str | None = None):
        self._base_url = (base_url or settings.go2rtc_url).rstrip("/")

    async def add_stream(self, name: str, rtsp_url: str) -> bool:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.put(
                f"{self._base_url}/api/streams",
                params={"name": name, "src": rtsp_url},
            )
            return resp.status_code in (200, 201)

    async def remove_stream(self, name: str) -> bool:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.delete(
                f"{self._base_url}/api/streams",
                params={"name": name},
            )
            return resp.status_code in (200, 204)

    async def list_streams(self) -> dict:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{self._base_url}/api/streams")
            resp.raise_for_status()
            return resp.json()

    async def get_webrtc_offer(self, stream_name: str, sdp_offer: str) -> str:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{self._base_url}/api/webrtc",
                params={"src": stream_name},
                content=sdp_offer,
                headers={"Content-Type": "application/sdp"},
            )
            resp.raise_for_status()
            return resp.text

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self._base_url}/api/streams")
                return resp.status_code == 200
        except Exception:
            return False
