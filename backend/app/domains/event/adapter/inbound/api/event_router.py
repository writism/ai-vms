from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.domains.event.adapter.inbound.api.dependencies import get_create_event_usecase, get_list_events_usecase
from app.domains.event.application.request.event_request import CreateEventRequest, ListEventsRequest
from app.domains.event.application.response.event_response import EventListResponse, EventResponse
from app.domains.event.application.usecase.event_usecase import CreateEventUseCase, ListEventsUseCase

router = APIRouter(prefix="/events", tags=["event"])


@router.post("", response_model=EventResponse, status_code=201)
async def create_event(
    request: CreateEventRequest,
    usecase: CreateEventUseCase = Depends(get_create_event_usecase),
) -> EventResponse:
    return await usecase.execute(request)


@router.get("", response_model=EventListResponse)
async def list_events(
    event_type: str | None = Query(None),
    camera_id: UUID | None = Query(None),
    identity_id: UUID | None = Query(None),
    from_date: datetime | None = Query(None),
    to_date: datetime | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    usecase: ListEventsUseCase = Depends(get_list_events_usecase),
) -> EventListResponse:
    request = ListEventsRequest(
        event_type=event_type,
        camera_id=camera_id,
        identity_id=identity_id,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
        offset=offset,
    )
    return await usecase.execute(request)
