from pydantic import BaseModel
from uuid import UUID


class RegisterIdentityRequest(BaseModel):
    name: str
    identity_type: str = "EMPLOYEE"
    department: str | None = None
    employee_id: str | None = None
    company: str | None = None
    visit_purpose: str | None = None
    notes: str | None = None


class UpdateIdentityRequest(BaseModel):
    name: str | None = None
    identity_type: str | None = None
    department: str | None = None
    employee_id: str | None = None
    company: str | None = None
    visit_purpose: str | None = None
    notes: str | None = None


class SearchFaceRequest(BaseModel):
    embedding: list[float]
    limit: int = 5
    threshold: float = 0.55


class RegisterFaceRequest(BaseModel):
    identity_id: UUID
    embedding: list[float]
    image_path: str | None = None
    quality_score: float = 0.0
