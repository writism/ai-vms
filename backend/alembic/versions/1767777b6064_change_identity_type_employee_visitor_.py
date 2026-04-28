"""change_identity_type_employee_visitor_add_company_visit_purpose

Revision ID: 1767777b6064
Revises: 001
Create Date: 2026-04-27 09:00:55.292911

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1767777b6064'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('identities', sa.Column('company', sa.String(length=100), nullable=True))
    op.add_column('identities', sa.Column('visit_purpose', sa.String(length=200), nullable=True))
    op.execute("UPDATE identities SET identity_type = 'EMPLOYEE' WHERE identity_type IN ('INTERNAL', 'VIP')")
    op.execute("UPDATE identities SET identity_type = 'VISITOR' WHERE identity_type IN ('EXTERNAL', 'BLACKLIST')")


def downgrade() -> None:
    op.execute("UPDATE identities SET identity_type = 'INTERNAL' WHERE identity_type = 'EMPLOYEE'")
    op.execute("UPDATE identities SET identity_type = 'EXTERNAL' WHERE identity_type = 'VISITOR'")
    op.drop_column('identities', 'visit_purpose')
    op.drop_column('identities', 'company')
