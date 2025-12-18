"""add phone_number to users

Revision ID: 00f5edf076f9
Revises: c3cd43a24d28
Create Date: 2025-11-22 11:06:55.886257

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '00f5edf076f9'
down_revision: Union[str, None] = 'c3cd43a24d28'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('phone_number', sa.String(length=20), nullable=True))
    op.create_index(op.f('ix_users_phone_number'), 'users', ['phone_number'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_users_phone_number'), table_name='users')
    op.drop_column('users', 'phone_number')

