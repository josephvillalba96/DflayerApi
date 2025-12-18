"""create audio_tracks table

Revision ID: 8b2d3c0d9def
Revises: 7a1c2f9b8abc
Create Date: 2025-12-18 00:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8b2d3c0d9def"
down_revision: Union[str, None] = "7a1c2f9b8abc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Crea la tabla audio_tracks según el modelo AudioTrack.
    """
    op.create_table(
        "audio_tracks",
        sa.Column("audio_id", sa.Integer(), primary_key=True, index=True),
        sa.Column("media_id", sa.Integer(), sa.ForeignKey("media_files.media_id"), nullable=True),
        sa.Column("post_id", sa.Integer(), sa.ForeignKey("contents.content_id"), nullable=True),
        sa.Column("title", sa.String(length=200), nullable=True),
        sa.Column("artist", sa.String(length=200), nullable=True),
        sa.Column("duration_seconds", sa.Float(), nullable=True),
        sa.Column("storage_path", sa.String(length=500), nullable=False),
        sa.Column("waveform_data", sa.Text(), nullable=True),
        sa.Column("format", sa.String(length=50), nullable=False),
        sa.Column("bitrate", sa.Integer(), nullable=True),
        sa.Column("sample_rate", sa.Integer(), nullable=True),
        sa.Column("is_original_audio", sa.Boolean(), nullable=True, server_default=sa.text("FALSE")),
        sa.Column("usage_count", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("created_at", sa.Date(), nullable=True),
        sa.Column("updated_at", sa.Date(), nullable=True),
    )
    op.create_index("ix_audio_tracks_audio_id", "audio_tracks", ["audio_id"], unique=False)


def downgrade() -> None:
    """
    Elimina la tabla audio_tracks.
    """
    op.drop_index("ix_audio_tracks_audio_id", table_name="audio_tracks")
    op.drop_table("audio_tracks")


