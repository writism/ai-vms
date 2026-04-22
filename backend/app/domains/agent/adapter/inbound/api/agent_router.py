from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.domains.agent.adapter.inbound.api.dependencies import get_run_pipeline_usecase
from app.domains.agent.application.usecase.run_agent_pipeline_usecase import RunAgentPipelineUseCase

router = APIRouter(prefix="/agent", tags=["agent"])


class AnalyzeRequest(BaseModel):
    camera_id: UUID


class AgentTaskResponse(BaseModel):
    id: str
    camera_id: str
    status: str
    severity: float
    summary: str | None
    actions_count: int
    error: str | None


@router.post("/analyze", response_model=AgentTaskResponse)
async def run_analysis(
    request: AnalyzeRequest,
    usecase: RunAgentPipelineUseCase = Depends(get_run_pipeline_usecase),
) -> AgentTaskResponse:
    task = await usecase.execute(request.camera_id)
    return AgentTaskResponse(
        id=str(task.id),
        camera_id=str(task.camera_id),
        status=task.status.value,
        severity=task.severity,
        summary=task.summary,
        actions_count=task.actions_count,
        error=task.error,
    )
