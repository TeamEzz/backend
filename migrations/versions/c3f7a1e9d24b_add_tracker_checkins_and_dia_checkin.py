"""add check_ins table and metas_usuario.dia_checkin

Revision ID: c3f7a1e9d24b
Revises: 9a1c4f2b6d3e
Create Date: 2026-06-09 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c3f7a1e9d24b"
down_revision: Union[str, Sequence[str], None] = "9a1c4f2b6d3e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("metas_usuario", sa.Column("dia_checkin", sa.Integer(), nullable=True))

    op.create_table(
        "check_ins",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id"), nullable=False),
        sa.Column("meta_id", sa.Integer(), sa.ForeignKey("metas_usuario.id"), nullable=False),
        sa.Column("mes", sa.Integer(), nullable=False),
        sa.Column("anio", sa.Integer(), nullable=False),
        sa.Column("monto_aportado", sa.Float(), nullable=False),
        sa.Column("objetivo_mes", sa.Float(), nullable=False),
        sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("usuario_id", "mes", "anio", name="uq_checkin_usuario_mes_anio"),
    )
    op.create_index("ix_check_ins_usuario_id", "check_ins", ["usuario_id"])
    op.create_index("ix_check_ins_meta_id", "check_ins", ["meta_id"])


def downgrade() -> None:
    op.drop_index("ix_check_ins_meta_id", table_name="check_ins")
    op.drop_index("ix_check_ins_usuario_id", table_name="check_ins")
    op.drop_table("check_ins")
    op.drop_column("metas_usuario", "dia_checkin")
