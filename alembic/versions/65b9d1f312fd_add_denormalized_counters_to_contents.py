"""add denormalized counters to contents

Revision ID: 65b9d1f312fd
Revises: 4898f0005ee2
Create Date: 2025-11-26 09:56:14.605251

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '65b9d1f312fd'
down_revision: Union[str, None] = '4898f0005ee2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('contents', sa.Column('view_count', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('contents', sa.Column('like_count', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('contents', sa.Column('comment_count', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('contents', sa.Column('share_count', sa.Integer(), nullable=True, server_default='0'))


def downgrade() -> None:
    op.drop_column('contents', 'share_count')
    op.drop_column('contents', 'comment_count')
    op.drop_column('contents', 'like_count')
    op.drop_column('contents', 'view_count')

