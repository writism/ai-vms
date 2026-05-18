"""encrypt camera rtsp credentials

Revision ID: e2f3a4b5c6d7
Revises: d1e2f3a4b5c6
Create Date: 2026-05-18 00:01:00.000000
"""
import logging
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "e2f3a4b5c6d7"
down_revision: Union[str, None] = "d1e2f3a4b5c6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

logger = logging.getLogger(__name__)


def upgrade() -> None:
    try:
        import os
        encryption_key = os.environ.get("ENCRYPTION_KEY", "")
        if not encryption_key:
            logger.warning("ENCRYPTION_KEY not set — skipping RTSP credential encryption migration")
            return

        from app.infrastructure.crypto.encryption import encrypt, is_encrypted

        conn = op.get_bind()
        rows = conn.execute(sa.text("SELECT id, rtsp_url FROM cameras WHERE rtsp_url IS NOT NULL")).fetchall()
        for row in rows:
            camera_id, rtsp_url = row
            if rtsp_url and not is_encrypted(rtsp_url):
                encrypted = encrypt(rtsp_url, encryption_key)
                conn.execute(
                    sa.text("UPDATE cameras SET rtsp_url = :url WHERE id = :id"),
                    {"url": encrypted, "id": camera_id},
                )
        logger.info("Encrypted %d camera RTSP URLs", len(rows))
    except Exception as exc:
        logger.warning("RTSP encryption migration failed (non-fatal): %s", exc)


def downgrade() -> None:
    try:
        import os
        encryption_key = os.environ.get("ENCRYPTION_KEY", "")
        if not encryption_key:
            return

        from app.infrastructure.crypto.encryption import decrypt, is_encrypted

        conn = op.get_bind()
        rows = conn.execute(sa.text("SELECT id, rtsp_url FROM cameras WHERE rtsp_url IS NOT NULL")).fetchall()
        for row in rows:
            camera_id, rtsp_url = row
            if rtsp_url and is_encrypted(rtsp_url):
                plain = decrypt(rtsp_url, encryption_key)
                conn.execute(
                    sa.text("UPDATE cameras SET rtsp_url = :url WHERE id = :id"),
                    {"url": plain, "id": camera_id},
                )
    except Exception as exc:
        logger.warning("RTSP decryption migration failed: %s", exc)
