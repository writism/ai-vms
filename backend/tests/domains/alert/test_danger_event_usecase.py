import pytest
from uuid import uuid4

from app.domains.alert.adapter.outbound.persistence.in_memory_danger_event_repository import InMemoryDangerEventRepository
from app.domains.alert.application.request.alert_request import (
    CreateDangerEventRequest,
    ListDangerEventsRequest,
    UpdateEventStatusRequest,
)
from app.domains.alert.application.usecase.danger_event_usecase import (
    CreateDangerEventUseCase,
    ListDangerEventsUseCase,
    UpdateEventStatusUseCase,
)


@pytest.fixture
def event_repo():
    return InMemoryDangerEventRepository()


@pytest.mark.anyio
async def test_create_danger_event(event_repo):
    usecase = CreateDangerEventUseCase(event_repo)
    camera_id = uuid4()

    result = await usecase.execute(
        CreateDangerEventRequest(
            camera_id=camera_id,
            danger_type="FIRE",
            severity="HIGH",
            confidence=0.92,
            description="화재 감지",
        )
    )

    assert result.danger_type == "FIRE"
    assert result.severity == "HIGH"
    assert result.status == "PENDING"
    assert result.confidence == 0.92


@pytest.mark.anyio
async def test_list_danger_events(event_repo):
    usecase = CreateDangerEventUseCase(event_repo)
    camera_id = uuid4()

    await usecase.execute(CreateDangerEventRequest(camera_id=camera_id, danger_type="FIRE", severity="HIGH", confidence=0.9))
    await usecase.execute(CreateDangerEventRequest(camera_id=camera_id, danger_type="SMOKE", severity="MEDIUM", confidence=0.7))

    list_uc = ListDangerEventsUseCase(event_repo)
    result = await list_uc.execute(ListDangerEventsRequest())

    assert result.total == 2
    assert len(result.items) == 2


@pytest.mark.anyio
async def test_list_with_filter(event_repo):
    usecase = CreateDangerEventUseCase(event_repo)
    camera_id = uuid4()

    await usecase.execute(CreateDangerEventRequest(camera_id=camera_id, danger_type="FIRE", severity="HIGH", confidence=0.9))
    await usecase.execute(CreateDangerEventRequest(camera_id=camera_id, danger_type="SMOKE", severity="LOW", confidence=0.5))

    list_uc = ListDangerEventsUseCase(event_repo)
    result = await list_uc.execute(ListDangerEventsRequest(danger_type="FIRE"))

    assert result.total == 1
    assert result.items[0].danger_type == "FIRE"


@pytest.mark.anyio
async def test_update_event_status(event_repo):
    create_uc = CreateDangerEventUseCase(event_repo)
    camera_id = uuid4()
    created = await create_uc.execute(
        CreateDangerEventRequest(camera_id=camera_id, danger_type="VIOLENCE", severity="CRITICAL", confidence=0.95)
    )

    update_uc = UpdateEventStatusUseCase(event_repo)
    result = await update_uc.execute(
        created.id,
        UpdateEventStatusRequest(status="ACKNOWLEDGED"),
    )

    assert result is not None
    assert result.status == "ACKNOWLEDGED"
