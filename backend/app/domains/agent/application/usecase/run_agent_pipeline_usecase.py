from datetime import datetime
from uuid import UUID

from app.domains.agent.domain.entity.agent_task import AgentTask, AgentTaskStatus
from app.domains.camera.application.port.camera_repository_port import CameraRepositoryPort
from app.infrastructure.ai.frame_capture import frame_capture_service


class RunAgentPipelineUseCase:
    def __init__(self, camera_repo: CameraRepositoryPort):
        self._camera_repo = camera_repo

    async def execute(self, camera_id: UUID) -> AgentTask:
        task = AgentTask(camera_id=camera_id, status=AgentTaskStatus.RUNNING)

        camera = await self._camera_repo.find_by_id(camera_id)
        if camera is None:
            task.status = AgentTaskStatus.FAILED
            task.error = "Camera not found"
            return task

        frame_data: bytes | None = None
        if camera.rtsp_url:
            captured = await frame_capture_service.capture_frame(camera.rtsp_url, str(camera_id))
            if captured is not None:
                import cv2
                _, encoded = cv2.imencode(".jpg", captured.frame)
                frame_data = encoded.tobytes()

        try:
            from app.infrastructure.langgraph.runner import run_analysis

            result = await run_analysis(str(camera_id), frame_data)

            task.severity = result.get("severity", 0.0)
            task.actions_count = len(result.get("actions", []))
            analysis = result.get("analysis")
            task.summary = analysis.summary if analysis else None
            task.error = result.get("error")
            task.status = AgentTaskStatus.FAILED if task.error else AgentTaskStatus.COMPLETED
        except Exception as e:
            task.status = AgentTaskStatus.FAILED
            task.error = str(e)

        task.completed_at = datetime.now()
        return task
