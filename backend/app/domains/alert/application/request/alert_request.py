from pydantic import BaseModel
from uuid import UUID


class CreateDangerEventRequest(BaseModel):
    camera_id: UUID
    danger_type: str
    severity: str
    confidence: float
    description: str | None = None
    snapshot_path: str | None = None


class UpdateEventStatusRequest(BaseModel):
    status: str
    resolved_by: UUID | None = None


class CreateAlertRuleRequest(BaseModel):
    name: str
    danger_types: list[str]
    min_severity: str
    camera_id: UUID | None = None
    notify_websocket: bool = True
    notify_mqtt: bool = False
    notify_email: bool = False
    email_recipients: list[str] = []
    enable_face_recognition: bool = False


class UpdateAlertRuleRequest(BaseModel):
    name: str | None = None
    camera_id: UUID | None = None
    danger_types: list[str] | None = None
    min_severity: str | None = None
    notify_websocket: bool | None = None
    notify_mqtt: bool | None = None
    notify_email: bool | None = None
    email_recipients: list[str] | None = None
    enable_face_recognition: bool | None = None
    is_active: bool | None = None


class ListDangerEventsRequest(BaseModel):
    danger_type: str | None = None
    severity: str | None = None
    status: str | None = None
    camera_id: UUID | None = None
    limit: int = 50
    offset: int = 0
