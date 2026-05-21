"""camera FK ON DELETE SET NULL for events, danger_events, recognition_logs

Revision ID: a2b3c4d5e6f7
Revises: f1a2b3c4d5e6
Create Date: 2026-05-21

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a2b3c4d5e6f7"
down_revision: Union[str, None] = "f1a2b3c4d5e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # danger_events.camera_id: NOT NULL → NULL + ON DELETE SET NULL
    op.alter_column("danger_events", "camera_id", nullable=True)
    op.drop_constraint("danger_events_camera_id_fkey", "danger_events", type_="foreignkey")
    op.create_foreign_key(
        "danger_events_camera_id_fkey",
        "danger_events", "cameras",
        ["camera_id"], ["id"],
        ondelete="SET NULL",
    )

    # events.camera_id: already nullable, just change action
    op.drop_constraint("events_camera_id_fkey", "events", type_="foreignkey")
    op.create_foreign_key(
        "events_camera_id_fkey",
        "events", "cameras",
        ["camera_id"], ["id"],
        ondelete="SET NULL",
    )

    # recognition_logs.camera_id: ON DELETE SET NULL
    op.drop_constraint("recognition_logs_camera_id_fkey", "recognition_logs", type_="foreignkey")
    op.create_foreign_key(
        "recognition_logs_camera_id_fkey",
        "recognition_logs", "cameras",
        ["camera_id"], ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("recognition_logs_camera_id_fkey", "recognition_logs", type_="foreignkey")
    op.create_foreign_key(
        "recognition_logs_camera_id_fkey",
        "recognition_logs", "cameras",
        ["camera_id"], ["id"],
    )

    op.drop_constraint("events_camera_id_fkey", "events", type_="foreignkey")
    op.create_foreign_key(
        "events_camera_id_fkey",
        "events", "cameras",
        ["camera_id"], ["id"],
    )

    op.drop_constraint("danger_events_camera_id_fkey", "danger_events", type_="foreignkey")
    op.create_foreign_key(
        "danger_events_camera_id_fkey",
        "danger_events", "cameras",
        ["camera_id"], ["id"],
    )
    op.alter_column("danger_events", "camera_id", nullable=False)
