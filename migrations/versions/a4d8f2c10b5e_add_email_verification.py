"""add email verification fields to usuarios

Revision ID: a4d8f2c10b5e
Revises: c3f7a1e9d24b
Create Date: 2026-06-12 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a4d8f2c10b5e"
down_revision: Union[str, Sequence[str], None] = "c3f7a1e9d24b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "usuarios",
        sa.Column("verificado", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )
    op.add_column("usuarios", sa.Column("codigo_verificacion", sa.String(), nullable=True))
    op.add_column("usuarios", sa.Column("codigo_expira_en", sa.DateTime(timezone=True), nullable=True))
    op.add_column("usuarios", sa.Column("codigo_enviado_en", sa.DateTime(timezone=True), nullable=True))
    op.add_column(
        "usuarios",
        sa.Column("codigo_intentos", sa.Integer(), server_default=sa.text("0"), nullable=False),
    )

    # Backfill: los usuarios existentes (anteriores a la verificación) se consideran verificados,
    # de lo contrario el bloqueo "block-until-verified" los dejaría sin poder iniciar sesión.
    op.execute("UPDATE usuarios SET verificado = true")


def downgrade() -> None:
    op.drop_column("usuarios", "codigo_intentos")
    op.drop_column("usuarios", "codigo_enviado_en")
    op.drop_column("usuarios", "codigo_expira_en")
    op.drop_column("usuarios", "codigo_verificacion")
    op.drop_column("usuarios", "verificado")
