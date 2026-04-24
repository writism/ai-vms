import logging
from dataclasses import dataclass

import httpx

from app.infrastructure.config.settings import settings

logger = logging.getLogger(__name__)

_DEFAULT_TIMEOUT = 3.0


@dataclass
class Go2RtcStream:
    name: str
    producers: list[dict]


class Go2RtcClient:
    _shared_client: httpx.AsyncClient | None = None

    def __init__(self, base_url: str | None = None):
        self._base_url = (base_url or settings.go2rtc_url).rstrip("/")

    def _client(self) -> httpx.AsyncClient:
        if Go2RtcClient._shared_client is None or Go2RtcClient._shared_client.is_closed:
            Go2RtcClient._shared_client = httpx.AsyncClient(timeout=_DEFAULT_TIMEOUT)
        return Go2RtcClient._shared_client

    async def add_stream(self, name: str, rtsp_url: str) -> bool:
        resp = await self._client().put(
            f"{self._base_url}/api/streams",
            params={"name": name, "src": rtsp_url},
        )
        return resp.status_code in (200, 201)

    async def restart_stream(self, name: str, rtsp_url: str) -> bool:
        await self.remove_stream(name)
        return await self.add_stream(name, rtsp_url)

    async def remove_stream(self, name: str) -> bool:
        resp = await self._client().delete(
            f"{self._base_url}/api/streams",
            params={"name": name},
        )
        return resp.status_code in (200, 204)

    async def list_streams(self) -> dict:
        resp = await self._client().get(f"{self._base_url}/api/streams")
        resp.raise_for_status()
        return resp.json()

    async def get_webrtc_offer(self, stream_name: str, sdp_offer: str) -> str:
        try:
            resp = await self._client().post(
                f"{self._base_url}/api/webrtc",
                params={"src": stream_name},
                content=sdp_offer,
                headers={"Content-Type": "application/sdp"},
            )
            resp.raise_for_status()
            return resp.text
        except httpx.HTTPStatusError as e:
            logger.error("go2rtc webrtc error %s for stream %s", e.response.status_code, stream_name)
            raise
        except httpx.ConnectError:
            logger.error("go2rtc unreachable at %s", self._base_url)
            raise

    async def health_check(self) -> bool:
        try:
            resp = await self._client().get(f"{self._base_url}/api/streams")
            return resp.status_code == 200
        except Exception:
            return False
