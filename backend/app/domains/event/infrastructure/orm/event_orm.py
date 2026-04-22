from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.session import Base


class EventORM(Base):
    __tablename__ = "events"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    event_type: Mapped[str] = mapped_column(String(30), index=True)
    camera_id: Mapped[UUID | None] = mapped_column(ForeignKey("cameras.id"), nullable=True)
    identity_id: Mapped[UUID | None] = mapped_column(ForeignKey("identities.id"), nullable=True)
    danger_event_id: Mapped[UUID | None] = mapped_column(ForeignKey("danger_events.id"), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
    snapshot_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
