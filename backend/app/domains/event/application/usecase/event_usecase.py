from app.domains.event.application.port.event_repository_port import EventRepositoryPort
from app.domains.event.application.request.event_request import CreateEventRequest, ListEventsRequest
from app.domains.event.application.response.event_response import EventListResponse, EventResponse
from app.domains.event.domain.entity.event import Event, EventType


class CreateEventUseCase:
    def __init__(self, repo: EventRepositoryPort):
        self._repo = repo

    async def execute(self, request: CreateEventRequest) -> EventResponse:
        event = Event(
            event_type=EventType(request.event_type),
            camera_id=request.camera_id,
            identity_id=request.identity_id,
            danger_event_id=request.danger_event_id,
            description=request.description,
            metadata=request.metadata,
            snapshot_path=request.snapshot_path,
        )
        saved = await self._repo.save(event)
        return EventResponse.from_entity(saved)


class ListEventsUseCase:
    def __init__(self, repo: EventRepositoryPort):
        self._repo = repo

    async def execute(self, request: ListEventsRequest) -> EventListResponse:
        events = await self._repo.find_all(
            event_type=request.event_type,
            camera_id=request.camera_id,
            identity_id=request.identity_id,
            from_date=request.from_date,
            to_date=request.to_date,
            limit=request.limit,
            offset=request.offset,
        )
        total = await self._repo.count(
            event_type=request.event_type,
            camera_id=request.camera_id,
            from_date=request.from_date,
            to_date=request.to_date,
        )
        return EventListResponse(
            items=[EventResponse.from_entity(e) for e in events],
            total=total,
        )
