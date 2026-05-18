"""add system_settings table

Revision ID: d1e2f3a4b5c6
Revises: cfc80f71c49f
Create Date: 2026-05-18 00:00:00.000000
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d1e2f3a4b5c6"
down_revision: Union[str, None] = "cfc80f71c49f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "system_settings",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("key", sa.String(100), nullable=False),
        sa.Column("value", sa.String(2000), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key"),
    )


def downgrade() -> None:
    op.drop_table("system_settings")
