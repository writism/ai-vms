from app.domains.agent.application.usecase.run_agent_pipeline_usecase import RunAgentPipelineUseCase
from app.domains.camera.adapter.outbound.persistence.in_memory_camera_repository import InMemoryCameraRepository

_camera_repo = InMemoryCameraRepository()


def get_run_pipeline_usecase() -> RunAgentPipelineUseCase:
    return RunAgentPipelineUseCase(_camera_repo)
