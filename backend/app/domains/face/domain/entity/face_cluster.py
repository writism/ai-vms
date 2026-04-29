from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


class ClusterStatus(StrEnum):
    PENDING = "PENDING"
    REGISTERED = "REGISTERED"
    IGNORED = "IGNORED"


@dataclass
class FaceCluster:
    representative_embedding: list[float]
    representative_image_path: str | None = None
    representative_quality_score: float = 0.0
    last_seen: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_camera_id: UUID | None = None
    status: ClusterStatus = ClusterStatus.PENDING
    linked_identity_id: UUID | None = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
