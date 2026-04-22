from app.domains.auth.domain.entity.user import User, UserRole
from app.domains.auth.infrastructure.orm.user_orm import UserORM


class UserMapper:
    @staticmethod
    def to_entity(orm: UserORM) -> User:
        return User(
            id=orm.id,
            email=orm.email,
            hashed_password=orm.hashed_password,
            name=orm.name,
            role=UserRole(orm.role),
            is_active=orm.is_active,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    @staticmethod
    def to_orm(entity: User) -> UserORM:
        return UserORM(
            id=entity.id,
            email=entity.email,
            hashed_password=entity.hashed_password,
            name=entity.name,
            role=entity.role.value,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
