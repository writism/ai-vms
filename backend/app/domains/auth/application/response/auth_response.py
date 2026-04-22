from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.domains.auth.domain.entity.user import User, UserRole


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: UUID
    email: str
    name: str
    role: UserRole
    is_active: bool
    created_at: datetime

    @staticmethod
    def from_entity(entity: User) -> "UserResponse":
        return UserResponse(
            id=entity.id,
            email=entity.email,
            name=entity.name,
            role=entity.role,
            is_active=entity.is_active,
            created_at=entity.created_at,
        )
