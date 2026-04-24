from app.domains.stream.application.port.stream_port import StreamPort
from app.domains.stream.application.request.stream_request import RegisterStreamRequest, WebRTCOfferRequest
from app.domains.stream.application.response.stream_response import (
    CameraConflictResponse,
    MediaServerResponse,
    MediaServerScanResponse,
    MediaServerStreamResponse,
    StreamListResponse,
    StreamRegistrationResponse,
    WebRTCAnswerResponse,
)


class RegisterStreamUseCase:
    def __init__(self, stream_service: StreamPort):
        self._stream = stream_service

    async def execute(self, request: RegisterStreamRequest) -> StreamRegistrationResponse:
        success = await self._stream.register_stream(request.camera_id, request.rtsp_url)
        return StreamRegistrationResponse(stream_name=request.camera_id, success=success)


class UnregisterStreamUseCase:
    def __init__(self, stream_service: StreamPort):
        self._stream = stream_service

    async def execute(self, stream_name: str) -> StreamRegistrationResponse:
        success = await self._stream.unregister_stream(stream_name)
        return StreamRegistrationResponse(stream_name=stream_name, success=success)


class ListStreamsUseCase:
    def __init__(self, stream_service: StreamPort):
        self._stream = stream_service

    async def execute(self) -> StreamListResponse:
        streams = await self._stream.list_streams()
        return StreamListResponse(streams=streams)


class WebRTCOfferUseCase:
    def __init__(self, stream_service: StreamPort):
        self._stream = stream_service

    async def execute(self, request: WebRTCOfferRequest) -> WebRTCAnswerResponse:
        from app.infrastructure.errors import ExternalServiceError

        try:
            answer = await self._stream.webrtc_offer(request.stream_name, request.sdp_offer)
        except Exception as e:
            raise ExternalServiceError("go2rtc", str(e))
        return WebRTCAnswerResponse(sdp_answer=answer)


class ScanMediaServersUseCase:
    def __init__(self, registered_camera_ips: set[str], own_server_ip: str | None):
        self._camera_ips = registered_camera_ips
        self._own_ip = own_server_ip

    async def execute(self, subnet: str) -> MediaServerScanResponse:
        from app.infrastructure.network.media_server_scanner import (
            detect_conflicts,
            scan_media_servers,
        )

        servers = await scan_media_servers(subnet, own_server_ip=self._own_ip)
        conflicts = detect_conflicts(servers, self._camera_ips)
        return MediaServerScanResponse(
            servers=[
                MediaServerResponse(
                    ip=s.ip, port=s.port, reachable=s.reachable, is_own=s.is_own,
                    streams=[
                        MediaServerStreamResponse(name=st.name, url=st.url, camera_ip=st.camera_ip)
                        for st in s.streams
                    ],
                )
                for s in servers
            ],
            conflicts=[
                CameraConflictResponse(camera_ip=c.camera_ip, servers=c.servers)
                for c in conflicts
            ],
            own_server_ip=self._own_ip,
        )
