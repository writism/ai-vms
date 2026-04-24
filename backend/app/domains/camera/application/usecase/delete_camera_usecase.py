from uuid import UUID

from app.domains.alert.application.port.danger_event_repository_port import DangerEventRepositoryPort
from app.domains.camera.application.port.camera_repository_port import CameraRepositoryPort
from app.domains.event.application.port.event_repository_port import EventRepositoryPort
from app.domains.stream.application.port.stream_port import StreamPort
from app.infrastructure.errors import ConflictError, NotFoundError


class DeleteCameraUseCase:
    def __init__(
        self,
        camera_repo: CameraRepositoryPort,
        danger_event_repo: DangerEventRepositoryPort,
        event_repo: EventRepositoryPort,
        stream_port: StreamPort,
    ):
        self._camera_repo = camera_repo
        self._danger_event_repo = danger_event_repo
        self._event_repo = event_repo
        self._stream_port = stream_port

    async def execute(self, camera_id: UUID) -> None:
        camera = await self._camera_repo.find_by_id(camera_id)
        if camera is None:
            raise NotFoundError("카메라를 찾을 수 없습니다")

        danger_count = await self._danger_event_repo.count(camera_id=camera_id)
        if danger_count > 0:
            raise ConflictError(f"이 카메라에 연결된 위험 이벤트가 {danger_count}건 있어 삭제할 수 없습니다")

        event_count = await self._event_repo.count(camera_id=camera_id)
        if event_count > 0:
            raise ConflictError(f"이 카메라에 연결된 이벤트가 {event_count}건 있어 삭제할 수 없습니다")

        try:
            await self._stream_port.unregister_stream(str(camera_id))
        except Exception:
            pass

        await self._camera_repo.delete(camera_id)
