"""add position to identities

Revision ID: a1b2c3d4e5f6
Revises: 9f1a2b3c4d5e
Create Date: 2026-04-30 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'a1b2c3d4e5f6'
down_revision = '9f1a2b3c4d5e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('identities', sa.Column('position', sa.String(100), nullable=True))


def downgrade() -> None:
    op.drop_column('identities', 'position')
