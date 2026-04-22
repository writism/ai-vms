from uuid import UUID

from app.domains.alert.application.port.danger_event_repository_port import DangerEventRepositoryPort
from app.domains.alert.application.request.alert_request import (
    CreateDangerEventRequest,
    ListDangerEventsRequest,
    UpdateEventStatusRequest,
)
from app.domains.alert.application.response.alert_response import DangerEventListResponse, DangerEventResponse
from app.domains.alert.domain.entity.danger_event import DangerEvent, DangerType, EventStatus, Severity


class CreateDangerEventUseCase:
    def __init__(self, repo: DangerEventRepositoryPort):
        self._repo = repo

    async def execute(self, request: CreateDangerEventRequest) -> DangerEventResponse:
        event = DangerEvent(
            camera_id=request.camera_id,
            danger_type=DangerType(request.danger_type),
            severity=Severity(request.severity),
            confidence=request.confidence,
            description=request.description,
            snapshot_path=request.snapshot_path,
        )
        saved = await self._repo.save(event)
        response = DangerEventResponse.from_entity(saved)

        from app.infrastructure.event_bus.ws_manager import ws_manager
        await ws_manager.broadcast({
            "type": "DANGER_EVENT",
            "data": response.model_dump(mode="json"),
        })

        return response


class ListDangerEventsUseCase:
    def __init__(self, repo: DangerEventRepositoryPort):
        self._repo = repo

    async def execute(self, request: ListDangerEventsRequest) -> DangerEventListResponse:
        events = await self._repo.find_all(
            danger_type=request.danger_type,
            severity=request.severity,
            status=request.status,
            camera_id=request.camera_id,
            limit=request.limit,
            offset=request.offset,
        )
        total = await self._repo.count(
            danger_type=request.danger_type,
            severity=request.severity,
            status=request.status,
        )
        return DangerEventListResponse(
            items=[DangerEventResponse.from_entity(e) for e in events],
            total=total,
        )


class UpdateEventStatusUseCase:
    def __init__(self, repo: DangerEventRepositoryPort):
        self._repo = repo

    async def execute(self, event_id: UUID, request: UpdateEventStatusRequest) -> DangerEventResponse | None:
        event = await self._repo.find_by_id(event_id)
        if event is None:
            return None

        new_status = EventStatus(request.status)
        if new_status == EventStatus.ACKNOWLEDGED:
            event.acknowledge()
        elif new_status == EventStatus.RESOLVED and request.resolved_by:
            event.resolve(request.resolved_by)
        elif new_status == EventStatus.FALSE_ALARM and request.resolved_by:
            event.mark_false_alarm(request.resolved_by)

        saved = await self._repo.save(event)
        return DangerEventResponse.from_entity(saved)
