from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4


class DangerType(StrEnum):
    FIRE = "FIRE"
    SMOKE = "SMOKE"
    VIOLENCE = "VIOLENCE"
    FIGHT = "FIGHT"
    WEAPON = "WEAPON"
    FALL = "FALL"
    INTRUSION = "INTRUSION"


class Severity(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class EventStatus(StrEnum):
    PENDING = "PENDING"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"
    FALSE_ALARM = "FALSE_ALARM"


@dataclass
class DangerEvent:
    camera_id: UUID
    danger_type: DangerType
    severity: Severity
    confidence: float
    description: str | None = None
    snapshot_path: str | None = None
    status: EventStatus = EventStatus.PENDING
    resolved_by: UUID | None = None
    resolved_at: datetime | None = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.now)

    def acknowledge(self) -> None:
        self.status = EventStatus.ACKNOWLEDGED

    def resolve(self, user_id: UUID) -> None:
        self.status = EventStatus.RESOLVED
        self.resolved_by = user_id
        self.resolved_at = datetime.now()

    def mark_false_alarm(self, user_id: UUID) -> None:
        self.status = EventStatus.FALSE_ALARM
        self.resolved_by = user_id
        self.resolved_at = datetime.now()
