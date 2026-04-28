from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


class IdentityType(StrEnum):
    EMPLOYEE = "EMPLOYEE"
    VISITOR = "VISITOR"


@dataclass
class Identity:
    name: str
    identity_type: IdentityType = IdentityType.EMPLOYEE
    department: str | None = None
    employee_id: str | None = None
    company: str | None = None
    visit_purpose: str | None = None
    notes: str | None = None
    face_image_url: str | None = None
    is_active: bool = True
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
