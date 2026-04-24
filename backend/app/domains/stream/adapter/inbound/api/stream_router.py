from fastapi import APIRouter, Depends

from app.domains.stream.adapter.inbound.api.dependencies import (
    get_list_streams_usecase,
    get_register_stream_usecase,
    get_scan_media_servers_usecase,
    get_unregister_stream_usecase,
    get_webrtc_offer_usecase,
)
from app.domains.stream.application.request.stream_request import (
    RegisterStreamRequest,
    ScanMediaServersRequest,
    WebRTCOfferRequest,
)
from app.domains.stream.application.response.stream_response import (
    MediaServerScanResponse,
    StreamListResponse,
    StreamRegistrationResponse,
    WebRTCAnswerResponse,
)
from app.domains.stream.application.usecase.stream_usecase import (
    ListStreamsUseCase,
    RegisterStreamUseCase,
    ScanMediaServersUseCase,
    UnregisterStreamUseCase,
    WebRTCOfferUseCase,
)

router = APIRouter(prefix="/streams", tags=["stream"])


@router.post("", response_model=StreamRegistrationResponse, status_code=201)
async def register_stream(
    request: RegisterStreamRequest,
    usecase: RegisterStreamUseCase = Depends(get_register_stream_usecase),
) -> StreamRegistrationResponse:
    return await usecase.execute(request)


@router.delete("/{stream_name}", response_model=StreamRegistrationResponse)
async def unregister_stream(
    stream_name: str,
    usecase: UnregisterStreamUseCase = Depends(get_unregister_stream_usecase),
) -> StreamRegistrationResponse:
    return await usecase.execute(stream_name)


@router.get("", response_model=StreamListResponse)
async def list_streams(
    usecase: ListStreamsUseCase = Depends(get_list_streams_usecase),
) -> StreamListResponse:
    return await usecase.execute()


@router.post("/webrtc", response_model=WebRTCAnswerResponse)
async def webrtc_offer(
    request: WebRTCOfferRequest,
    usecase: WebRTCOfferUseCase = Depends(get_webrtc_offer_usecase),
) -> WebRTCAnswerResponse:
    return await usecase.execute(request)


@router.post("/media-servers/scan", response_model=MediaServerScanResponse)
async def scan_media_servers(
    request: ScanMediaServersRequest,
    usecase: ScanMediaServersUseCase = Depends(get_scan_media_servers_usecase),
) -> MediaServerScanResponse:
    return await usecase.execute(request.subnet)
