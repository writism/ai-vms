from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class AlertRule:
    name: str
    danger_types: list[str]
    min_severity: str
    notify_websocket: bool = True
    notify_mqtt: bool = False
    notify_email: bool = False
    email_recipients: list[str] = field(default_factory=list)
    is_active: bool = True
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
