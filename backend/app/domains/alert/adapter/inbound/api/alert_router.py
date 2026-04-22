from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from app.domains.alert.adapter.inbound.api.dependencies import (
    get_create_alert_rule_usecase,
    get_create_danger_event_usecase,
    get_delete_alert_rule_usecase,
    get_list_alert_rules_usecase,
    get_list_danger_events_usecase,
    get_update_event_status_usecase,
)
from app.domains.alert.application.request.alert_request import (
    CreateAlertRuleRequest,
    CreateDangerEventRequest,
    ListDangerEventsRequest,
    UpdateEventStatusRequest,
)
from app.domains.alert.application.response.alert_response import (
    AlertRuleResponse,
    DangerEventListResponse,
    DangerEventResponse,
)
from app.domains.alert.application.usecase.alert_rule_usecase import (
    CreateAlertRuleUseCase,
    DeleteAlertRuleUseCase,
    ListAlertRulesUseCase,
)
from app.domains.alert.application.usecase.danger_event_usecase import (
    CreateDangerEventUseCase,
    ListDangerEventsUseCase,
    UpdateEventStatusUseCase,
)

router = APIRouter(prefix="/alerts", tags=["alert"])


@router.post("/events", response_model=DangerEventResponse, status_code=201)
async def create_danger_event(
    request: CreateDangerEventRequest,
    usecase: CreateDangerEventUseCase = Depends(get_create_danger_event_usecase),
) -> DangerEventResponse:
    return await usecase.execute(request)


@router.get("/events", response_model=DangerEventListResponse)
async def list_danger_events(
    danger_type: str | None = Query(None),
    severity: str | None = Query(None),
    status: str | None = Query(None),
    camera_id: UUID | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    usecase: ListDangerEventsUseCase = Depends(get_list_danger_events_usecase),
) -> DangerEventListResponse:
    request = ListDangerEventsRequest(
        danger_type=danger_type,
        severity=severity,
        status=status,
        camera_id=camera_id,
        limit=limit,
        offset=offset,
    )
    return await usecase.execute(request)


@router.patch("/events/{event_id}", response_model=DangerEventResponse)
async def update_event_status(
    event_id: UUID,
    request: UpdateEventStatusRequest,
    usecase: UpdateEventStatusUseCase = Depends(get_update_event_status_usecase),
) -> DangerEventResponse:
    result = await usecase.execute(event_id, request)
    if result is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return result


@router.post("/rules", response_model=AlertRuleResponse, status_code=201)
async def create_alert_rule(
    request: CreateAlertRuleRequest,
    usecase: CreateAlertRuleUseCase = Depends(get_create_alert_rule_usecase),
) -> AlertRuleResponse:
    return await usecase.execute(request)


@router.get("/rules", response_model=list[AlertRuleResponse])
async def list_alert_rules(
    usecase: ListAlertRulesUseCase = Depends(get_list_alert_rules_usecase),
) -> list[AlertRuleResponse]:
    return await usecase.execute()


@router.delete("/rules/{rule_id}", status_code=204)
async def delete_alert_rule(
    rule_id: UUID,
    usecase: DeleteAlertRuleUseCase = Depends(get_delete_alert_rule_usecase),
) -> None:
    deleted = await usecase.execute(rule_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Rule not found")
