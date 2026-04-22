from app.domains.stream.adapter.outbound.external.go2rtc_stream_adapter import Go2RtcStreamAdapter
from app.domains.stream.application.usecase.stream_usecase import (
    ListStreamsUseCase,
    RegisterStreamUseCase,
    UnregisterStreamUseCase,
    WebRTCOfferUseCase,
)

_stream_adapter = Go2RtcStreamAdapter()


def get_register_stream_usecase() -> RegisterStreamUseCase:
    return RegisterStreamUseCase(_stream_adapter)


def get_unregister_stream_usecase() -> UnregisterStreamUseCase:
    return UnregisterStreamUseCase(_stream_adapter)


def get_list_streams_usecase() -> ListStreamsUseCase:
    return ListStreamsUseCase(_stream_adapter)


def get_webrtc_offer_usecase() -> WebRTCOfferUseCase:
    return WebRTCOfferUseCase(_stream_adapter)
