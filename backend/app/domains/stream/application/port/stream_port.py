from abc import ABC, abstractmethod


class StreamPort(ABC):
    @abstractmethod
    async def register_stream(self, name: str, rtsp_url: str) -> bool: ...

    @abstractmethod
    async def unregister_stream(self, name: str) -> bool: ...

    @abstractmethod
    async def list_streams(self) -> dict: ...

    @abstractmethod
    async def webrtc_offer(self, stream_name: str, sdp_offer: str) -> str: ...

    @abstractmethod
    async def get_active_stream_names(self) -> set[str]: ...
