from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.session import Base


class DangerEventORM(Base):
    __tablename__ = "danger_events"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    camera_id: Mapped[UUID] = mapped_column(ForeignKey("cameras.id"))
    danger_type: Mapped[str] = mapped_column(String(30))
    severity: Mapped[str] = mapped_column(String(20))
    confidence: Mapped[float] = mapped_column(Float)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    snapshot_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="PENDING")
    resolved_by: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AlertRuleORM(Base):
    __tablename__ = "alert_rules"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100))
    danger_types: Mapped[list[str]] = mapped_column(ARRAY(String(30)))
    min_severity: Mapped[str] = mapped_column(String(20))
    notify_websocket: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_mqtt: Mapped[bool] = mapped_column(Boolean, default=False)
    notify_email: Mapped[bool] = mapped_column(Boolean, default=False)
    email_recipients: Mapped[list[str]] = mapped_column(ARRAY(String(255)), default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
