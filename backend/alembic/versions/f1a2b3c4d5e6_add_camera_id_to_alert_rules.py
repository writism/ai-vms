"""add camera_id to alert_rules

Revision ID: f1a2b3c4d5e6
Revises: cfc80f71c49f
Create Date: 2026-05-20

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f1a2b3c4d5e6"
down_revision: Union[str, None] = "cc9d217e637c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "alert_rules",
        sa.Column("camera_id", sa.Uuid(), nullable=True),
    )
    op.create_foreign_key(
        "fk_alert_rules_camera_id",
        "alert_rules", "cameras",
        ["camera_id"], ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_alert_rules_camera_id", "alert_rules", type_="foreignkey")
    op.drop_column("alert_rules", "camera_id")
