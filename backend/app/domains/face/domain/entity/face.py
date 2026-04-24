from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4


@dataclass
class Face:
    identity_id: UUID | None
    embedding: list[float]
    image_path: str | None = None
    quality_score: float = 0.0
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
