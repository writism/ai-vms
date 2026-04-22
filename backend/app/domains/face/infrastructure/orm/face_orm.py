from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.session import Base


class IdentityORM(Base):
    __tablename__ = "identities"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100))
    identity_type: Mapped[str] = mapped_column(String(20), default="INTERNAL")
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)
    employee_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    faces: Mapped[list["FaceORM"]] = relationship(back_populates="identity", lazy="selectin")


class FaceORM(Base):
    __tablename__ = "faces"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    identity_id: Mapped[UUID | None] = mapped_column(ForeignKey("identities.id"), nullable=True)
    embedding: Mapped[list[float]] = mapped_column(ARRAY(Float))
    image_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    quality_score: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    identity: Mapped[IdentityORM | None] = relationship(back_populates="faces", lazy="selectin")
