"""add face_clusters and recognition_log embedding

Revision ID: 9f1a2b3c4d5e
Revises: cfc80f71c49f
Create Date: 2026-04-29 03:30:00.000000
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "9f1a2b3c4d5e"
down_revision: str | Sequence[str] | None = "cfc80f71c49f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "face_clusters",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("representative_embedding", postgresql.ARRAY(sa.Float()), nullable=False),
        sa.Column("representative_image_path", sa.String(500), nullable=True),
        sa.Column("representative_quality_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("last_seen", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("last_camera_id", sa.Uuid(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="PENDING"),
        sa.Column("linked_identity_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["last_camera_id"], ["cameras.id"]),
        sa.ForeignKeyConstraint(["linked_identity_id"], ["identities.id"]),
    )
    op.create_index("ix_face_clusters_status", "face_clusters", ["status"])
    op.create_index("ix_face_clusters_last_seen", "face_clusters", ["last_seen"])

    op.add_column("recognition_logs", sa.Column("embedding", postgresql.ARRAY(sa.Float()), nullable=True))
    op.add_column("recognition_logs", sa.Column("image_path", sa.String(500), nullable=True))
    op.add_column("recognition_logs", sa.Column("cluster_id", sa.Uuid(), nullable=True))
    op.create_foreign_key(
        "fk_recognition_logs_cluster_id",
        "recognition_logs",
        "face_clusters",
        ["cluster_id"],
        ["id"],
    )
    op.create_index("ix_recognition_logs_cluster_id", "recognition_logs", ["cluster_id"])
    op.create_index("ix_recognition_logs_created_at", "recognition_logs", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_recognition_logs_created_at", table_name="recognition_logs")
    op.drop_index("ix_recognition_logs_cluster_id", table_name="recognition_logs")
    op.drop_constraint("fk_recognition_logs_cluster_id", "recognition_logs", type_="foreignkey")
    op.drop_column("recognition_logs", "cluster_id")
    op.drop_column("recognition_logs", "image_path")
    op.drop_column("recognition_logs", "embedding")
    op.drop_index("ix_face_clusters_last_seen", table_name="face_clusters")
    op.drop_index("ix_face_clusters_status", table_name="face_clusters")
    op.drop_table("face_clusters")
