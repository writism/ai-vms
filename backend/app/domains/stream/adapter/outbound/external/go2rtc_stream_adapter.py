from app.domains.stream.application.port.stream_port import StreamPort
from app.infrastructure.go2rtc.go2rtc_client import Go2RtcClient


class Go2RtcStreamAdapter(StreamPort):
    def __init__(self, client: Go2RtcClient | None = None):
        self._client = client or Go2RtcClient()

    async def register_stream(self, name: str, rtsp_url: str) -> bool:
        return await self._client.add_stream(name, rtsp_url)

    async def unregister_stream(self, name: str) -> bool:
        return await self._client.remove_stream(name)

    async def list_streams(self) -> dict:
        return await self._client.list_streams()

    async def webrtc_offer(self, stream_name: str, sdp_offer: str) -> str:
        return await self._client.get_webrtc_offer(stream_name, sdp_offer)
