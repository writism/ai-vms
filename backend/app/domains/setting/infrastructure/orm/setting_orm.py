from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.session import Base


class SystemSettingORM(Base):
    __tablename__ = "system_settings"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    value: Mapped[str] = mapped_column(String(2000), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
