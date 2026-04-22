from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.session import Base


class NetworkORM(Base):
    __tablename__ = "networks"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100))
    subnet: Mapped[str] = mapped_column(String(50))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    cameras: Mapped[list["CameraORM"]] = relationship(back_populates="network", lazy="selectin")


class CameraORM(Base):
    __tablename__ = "cameras"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    network_id: Mapped[UUID | None] = mapped_column(ForeignKey("networks.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(100))
    ip_address: Mapped[str] = mapped_column(String(45), unique=True)
    status: Mapped[str] = mapped_column(String(20), default="OFFLINE")
    rtsp_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    onvif_port: Mapped[int] = mapped_column(Integer, default=80)
    manufacturer: Mapped[str | None] = mapped_column(String(100), nullable=True)
    model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    firmware_version: Mapped[str | None] = mapped_column(String(100), nullable=True)
    mac_address: Mapped[str | None] = mapped_column(String(17), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    network: Mapped[NetworkORM | None] = relationship(back_populates="cameras", lazy="selectin")
