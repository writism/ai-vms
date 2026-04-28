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
    company: str | None
    visit_purpose: str | None
    notes: str | None
    face_image_url: str | None
    is_active: bool
    created_at: datetime

    @staticmethod
    def from_entity(entity: Identity) -> "IdentityResponse":
        return IdentityResponse(
            id=entity.id,
            name=entity.name,
            identity_type=entity.identity_type,
            department=entity.department,
            employee_id=entity.employee_id,
            company=entity.company,
            visit_purpose=entity.visit_purpose,
            notes=entity.notes,
            face_image_url=entity.face_image_url,
            is_active=entity.is_active,
            created_at=entity.created_at,
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
    created_at: datetime
