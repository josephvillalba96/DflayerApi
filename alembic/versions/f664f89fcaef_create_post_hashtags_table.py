"""create post_hashtags table

Revision ID: f664f89fcaef
Revises: 65b9d1f312fd
Create Date: 2025-11-26 09:58:42.937977

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f664f89fcaef'
down_revision: Union[str, None] = '65b9d1f312fd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('post_hashtags',
    sa.Column('post_hashtag_id', sa.Integer(), nullable=False),
    sa.Column('post_id', sa.Integer(), nullable=False),
    sa.Column('hashtag', sa.String(length=100), nullable=False),
    sa.Column('created_at', sa.Date(), nullable=True),
    sa.ForeignKeyConstraint(['post_id'], ['contents.content_id'], ),
    sa.PrimaryKeyConstraint('post_hashtag_id')
    )
    op.create_index(op.f('ix_post_hashtags_post_hashtag_id'), 'post_hashtags', ['post_hashtag_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_post_hashtags_post_hashtag_id'), table_name='post_hashtags')
    op.drop_table('post_hashtags')

