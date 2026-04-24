from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


class IdentityType(StrEnum):
    INTERNAL = "INTERNAL"
    EXTERNAL = "EXTERNAL"
    VIP = "VIP"
    BLACKLIST = "BLACKLIST"


@dataclass
class Identity:
    name: str
    identity_type: IdentityType = IdentityType.INTERNAL
    department: str | None = None
    employee_id: str | None = None
    notes: str | None = None
    is_active: bool = True
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
