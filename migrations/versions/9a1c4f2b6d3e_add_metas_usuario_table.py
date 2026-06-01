"""add metas_usuario table

Revision ID: 9a1c4f2b6d3e
Revises: 5e2c1f0ad7a1
Create Date: 2026-06-01 14:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9a1c4f2b6d3e"
down_revision: Union[str, Sequence[str], None] = "5e2c1f0ad7a1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "metas_usuario",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id"), nullable=False),
        sa.Column("meta_titulo", sa.String(), nullable=False),
        sa.Column("meta_tag", sa.String(), nullable=True),
        sa.Column("es_custom", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("es_primaria", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("horizonte_meses", sa.Integer(), nullable=False),
        sa.Column("ingreso_mensual", sa.Float(), nullable=False),
        sa.Column("gastos_mensuales", sa.Float(), nullable=False),
        sa.Column("costo_meta", sa.Float(), nullable=False),
        sa.Column("ahorro_requerido", sa.Float(), nullable=False),
        sa.Column("pct_ingreso", sa.Float(), nullable=False),
        sa.Column("viabilidad", sa.String(), nullable=False),
        sa.Column("instrumento", sa.String(), nullable=False),
        sa.Column("mensaje_toro", sa.Text(), nullable=True),
        sa.Column("otras_metas_json", sa.Text(), nullable=True),
        sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_metas_usuario_usuario_id", "metas_usuario", ["usuario_id"])


def downgrade() -> None:
    op.drop_index("ix_metas_usuario_usuario_id", table_name="metas_usuario")
    op.drop_table("metas_usuario")
