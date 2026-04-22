from app.domains.stream.application.port.stream_port import StreamPort
from app.domains.stream.application.request.stream_request import RegisterStreamRequest, WebRTCOfferRequest
from app.domains.stream.application.response.stream_response import (
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
        answer = await self._stream.webrtc_offer(request.stream_name, request.sdp_offer)
        return WebRTCAnswerResponse(sdp_answer=answer)
