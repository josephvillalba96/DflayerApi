"""create_content_audio_track_many_to_many

Revision ID: 3518f054e2a6
Revises: f664f89fcaef
Create Date: 2025-12-16 14:57:50.465253

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3518f054e2a6'
# IMPORTANTE:
# La revisión anterior b23f2aeca807 no existe en el repositorio actual.
# Encadenamos esta migración al head real existente: f664f89fcaef
down_revision: Union[str, None] = 'f664f89fcaef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

