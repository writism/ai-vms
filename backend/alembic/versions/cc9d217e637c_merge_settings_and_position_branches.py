"""merge settings and position branches

Revision ID: cc9d217e637c
Revises: a1b2c3d4e5f6, e2f3a4b5c6d7
Create Date: 2026-05-18 08:51:38.145375

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cc9d217e637c'
down_revision: Union[str, None] = ('a1b2c3d4e5f6', 'e2f3a4b5c6d7')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
