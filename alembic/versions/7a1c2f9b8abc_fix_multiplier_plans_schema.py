"""fix multiplier_plans schema to match MembershipPlan model

Revision ID: 7a1c2f9b8abc
Revises: 3518f054e2a6
Create Date: 2025-12-18 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7a1c2f9b8abc"
down_revision: Union[str, None] = "3518f054e2a6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Alinea la tabla multiplier_plans con el modelo MembershipPlan:
    - Renombra columnas legacy:
        name -> plan_name
        multiplier_factor -> multiplier
    - Agrega columnas nuevas usadas por el modelo:
        duration_days, description, is_active, created_at, updated_at
    """
    # Renombrar columnas existentes si todavía tienen los nombres legacy
    with op.batch_alter_table("multiplier_plans") as batch_op:
        # IMPORTANTE: checkfirst no existe para rename, así que asumimos nombres legacy
        batch_op.alter_column("name", new_column_name="plan_name")
        batch_op.alter_column("multiplier_factor", new_column_name="multiplier")

        # Agregar nuevas columnas solo si no existen
        batch_op.add_column(
            sa.Column("duration_days", sa.Integer(), nullable=False, server_default="30")
        )
        batch_op.add_column(
            sa.Column("description", sa.String(length=500), nullable=True)
        )
        batch_op.add_column(
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("TRUE"))
        )
        batch_op.add_column(sa.Column("created_at", sa.Date(), nullable=True))
        batch_op.add_column(sa.Column("updated_at", sa.Date(), nullable=True))


def downgrade() -> None:
    """
    Revierte los cambios:
    - Elimina columnas nuevas
    - Renombra columnas de vuelta a los nombres legacy
    """
    with op.batch_alter_table("multiplier_plans") as batch_op:
        batch_op.drop_column("updated_at")
        batch_op.drop_column("created_at")
        batch_op.drop_column("is_active")
        batch_op.drop_column("description")
        batch_op.drop_column("duration_days")

        batch_op.alter_column("multiplier", new_column_name="multiplier_factor")
        batch_op.alter_column("plan_name", new_column_name="name")


