from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4


@dataclass
class RecognitionLog:
    camera_id: UUID
    identity_id: UUID | None
    identity_name: str
    identity_type: str
    confidence: float
    is_registered: bool = True
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
