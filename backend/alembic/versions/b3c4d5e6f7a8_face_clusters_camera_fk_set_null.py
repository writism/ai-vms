"""face_clusters.last_camera_id FK ON DELETE SET NULL

Revision ID: b3c4d5e6f7a8
Revises: a2b3c4d5e6f7
Create Date: 2026-05-21

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b3c4d5e6f7a8"
down_revision: Union[str, None] = "a2b3c4d5e6f7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("face_clusters_last_camera_id_fkey", "face_clusters", type_="foreignkey")
    op.create_foreign_key(
        "face_clusters_last_camera_id_fkey",
        "face_clusters", "cameras",
        ["last_camera_id"], ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("face_clusters_last_camera_id_fkey", "face_clusters", type_="foreignkey")
    op.create_foreign_key(
        "face_clusters_last_camera_id_fkey",
        "face_clusters", "cameras",
        ["last_camera_id"], ["id"],
    )
