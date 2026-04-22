import pytest
from uuid import uuid4

from app.domains.event.adapter.outbound.persistence.in_memory_event_repository import InMemoryEventRepository
from app.domains.event.application.request.event_request import CreateEventRequest, ListEventsRequest
from app.domains.event.application.usecase.event_usecase import CreateEventUseCase, ListEventsUseCase


@pytest.fixture
def event_repo():
    return InMemoryEventRepository()


@pytest.mark.anyio
async def test_create_event(event_repo):
    usecase = CreateEventUseCase(event_repo)
    camera_id = uuid4()

    result = await usecase.execute(
        CreateEventRequest(
            event_type="CAMERA_ONLINE",
            camera_id=camera_id,
            description="카메라 온라인 전환",
        )
    )

    assert result.event_type == "CAMERA_ONLINE"
    assert result.camera_id == camera_id


@pytest.mark.anyio
async def test_list_events_with_filter(event_repo):
    create_uc = CreateEventUseCase(event_repo)
    cam1 = uuid4()
    cam2 = uuid4()

    await create_uc.execute(CreateEventRequest(event_type="CAMERA_ONLINE", camera_id=cam1))
    await create_uc.execute(CreateEventRequest(event_type="FACE_RECOGNIZED", camera_id=cam1))
    await create_uc.execute(CreateEventRequest(event_type="CAMERA_ONLINE", camera_id=cam2))

    list_uc = ListEventsUseCase(event_repo)

    result = await list_uc.execute(ListEventsRequest(event_type="CAMERA_ONLINE"))
    assert result.total == 2

    result = await list_uc.execute(ListEventsRequest(camera_id=cam1))
    assert result.total == 2
