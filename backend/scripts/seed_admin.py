"""Create initial admin user for AI-VMS."""

import asyncio
import sys
from uuid import uuid4

import bcrypt
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.infrastructure.config.settings import settings

ADMIN_EMAIL = "admin@ai-vms.io"
ADMIN_PASSWORD = "admin1234!"
ADMIN_NAME = "관리자"


async def seed_admin() -> None:
    engine = create_async_engine(settings.database_url)
    hashed = bcrypt.hashpw(ADMIN_PASSWORD.encode(), bcrypt.gensalt()).decode()

    async with engine.begin() as conn:
        result = await conn.execute(
            text("SELECT id FROM users WHERE email = :email"),
            {"email": ADMIN_EMAIL},
        )
        if result.first():
            print(f"Admin user already exists: {ADMIN_EMAIL}")
            return

        await conn.execute(
            text(
                "INSERT INTO users (id, email, hashed_password, name, role, is_active) "
                "VALUES (:id, :email, :hashed_password, :name, :role, true)"
            ),
            {
                "id": str(uuid4()),
                "email": ADMIN_EMAIL,
                "hashed_password": hashed,
                "name": ADMIN_NAME,
                "role": "ADMIN",
            },
        )
        print(f"Admin user created: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_admin())
