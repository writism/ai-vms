from app.domains.face.domain.entity.face import Face
from app.domains.face.domain.entity.identity import Identity, IdentityType
from app.domains.face.infrastructure.orm.face_orm import FaceORM, IdentityORM


class IdentityMapper:
    @staticmethod
    def to_entity(orm: IdentityORM) -> Identity:
        face_image_url: str | None = None
        if orm.faces:
            for f in orm.faces:
                if f.image_path:
                    face_image_url = f"/{f.image_path}"
                    break
        return Identity(
            id=orm.id,
            name=orm.name,
            identity_type=IdentityType(orm.identity_type),
            department=orm.department,
            employee_id=orm.employee_id,
            company=orm.company,
            visit_purpose=orm.visit_purpose,
            notes=orm.notes,
            face_image_url=face_image_url,
            is_active=orm.is_active,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    @staticmethod
    def to_orm(entity: Identity) -> IdentityORM:
        return IdentityORM(
            id=entity.id,
            name=entity.name,
            identity_type=entity.identity_type.value,
            department=entity.department,
            employee_id=entity.employee_id,
            company=entity.company,
            visit_purpose=entity.visit_purpose,
            notes=entity.notes,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )


class FaceMapper:
    @staticmethod
    def to_entity(orm: FaceORM) -> Face:
        return Face(
            id=orm.id,
            identity_id=orm.identity_id,
            embedding=list(orm.embedding),
            image_path=orm.image_path,
            quality_score=orm.quality_score,
            created_at=orm.created_at,
        )

    @staticmethod
    def to_orm(entity: Face) -> FaceORM:
        return FaceORM(
            id=entity.id,
            identity_id=entity.identity_id,
            embedding=entity.embedding,
            image_path=entity.image_path,
            quality_score=entity.quality_score,
            created_at=entity.created_at,
        )
