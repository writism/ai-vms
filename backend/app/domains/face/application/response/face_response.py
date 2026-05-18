from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.domains.face.domain.entity.identity import Identity, IdentityType


class IdentityResponse(BaseModel):
    id: UUID
    name: str
    identity_type: IdentityType
    department: str | None
    employee_id: str | None
    position: str | None
    company: str | None
    visit_purpose: str | None
    notes: str | None
    face_image_url: str | None
    is_active: bool
    created_at: datetime
    is_duplicate: bool = False

    @staticmethod
    def from_entity(entity: Identity, is_duplicate: bool = False) -> "IdentityResponse":
        return IdentityResponse(
            id=entity.id,
            name=entity.name,
            identity_type=entity.identity_type,
            department=entity.department,
            employee_id=entity.employee_id,
            position=entity.position,
            company=entity.company,
            visit_purpose=entity.visit_purpose,
            notes=entity.notes,
            face_image_url=entity.face_image_url,
            is_active=entity.is_active,
            created_at=entity.created_at,
            is_duplicate=is_duplicate,
        )


class FaceMatchResponse(BaseModel):
    identity_id: UUID
    face_id: UUID
    score: float
    identity_name: str
    is_confirmed: bool
    needs_verification: bool


class RecognitionLogResponse(BaseModel):
    id: UUID
    camera_id: UUID
    identity_id: UUID | None
    identity_name: str
    identity_type: str
    confidence: float
    is_registered: bool
    image_url: str | None = None
    created_at: datetime


class FaceSuggestionResponse(BaseModel):
    cluster_id: UUID
    image_url: str | None
    count_window: int
    avg_confidence: float
    last_seen: datetime
    last_camera_id: UUID | None
    quality_score: float
    status: str


class ClusterSnapshotResponse(BaseModel):
    log_id: UUID
    image_url: str
    confidence: float
    created_at: datetime


class SimilarIdentityResponse(BaseModel):
    identity_id: UUID
    name: str
    position: str | None
    department: str | None
    identity_type: str
    face_image_url: str | None
    score: float


class FaceDetailResponse(BaseModel):
    face_id: UUID
    image_url: str | None
    quality_score: float
    created_at: datetime
    is_outlier: bool = False


class OutlierSnapshotResponse(BaseModel):
    log_id: UUID
    image_url: str
    confidence: float
    created_at: datetime
    is_outlier: bool
    similarity_to_mean: float
