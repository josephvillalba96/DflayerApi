"""add location column to contents

Revision ID: 4898f0005ee2
Revises: b58fc5ef8432
Create Date: 2025-11-26 09:51:54.069616

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4898f0005ee2'
down_revision: Union[str, None] = 'b58fc5ef8432'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create ENUM type first (using lowercase values to match model: DRAFT = "draft")
    sa.Enum('draft', 'processing', 'published', 'deleted', name='contentstatus').create(op.get_bind(), checkfirst=True)
    
    op.add_column('contents', sa.Column('location', sa.String(length=255), nullable=True))
    op.add_column('contents', sa.Column('is_monetizable', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('contents', sa.Column('status', sa.Enum('draft', 'processing', 'published', 'deleted', name='contentstatus'), nullable=True, server_default='draft'))
    op.add_column('contents', sa.Column('updated_at', sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column('contents', 'updated_at')
    op.drop_column('contents', 'status')
    op.drop_column('contents', 'is_monetizable')
    op.drop_column('contents', 'location')
    
    # Drop ENUM type
    sa.Enum('draft', 'processing', 'published', 'deleted', name='contentstatus').drop(op.get_bind(), checkfirst=True)

