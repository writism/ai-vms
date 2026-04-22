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
    notify_websocket: bool = True
    notify_mqtt: bool = False
    notify_email: bool = False
    email_recipients: list[str] = []


class ListDangerEventsRequest(BaseModel):
    danger_type: str | None = None
    severity: str | None = None
    status: str | None = None
    camera_id: UUID | None = None
    limit: int = 50
    offset: int = 0
