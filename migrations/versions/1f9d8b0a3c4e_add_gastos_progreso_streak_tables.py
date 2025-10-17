"""add gastos progreso streak tables

Revision ID: 1f9d8b0a3c4e
Revises: 7b1e03bfcb59
Create Date: 2025-03-05 21:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1f9d8b0a3c4e"
down_revision: Union[str, Sequence[str], None] = "7b1e03bfcb59"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "gastos",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id"), nullable=False),
        sa.Column("categoria", sa.String(), nullable=False),
        sa.Column("monto", sa.Float(), nullable=False),
        sa.Column("es_necesario", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("fecha", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_gasto_user_fecha", "gastos", ["usuario_id", "fecha"])
    op.create_index("ix_gasto_user_cat", "gastos", ["usuario_id", "categoria"])

    op.create_table(
        "progreso_leccion",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id"), nullable=False),
        sa.Column("leccion_id", sa.Integer(), nullable=False),
        sa.Column("completada", sa.Boolean(), server_default=sa.false(), nullable=False),
    )
    op.create_index("ix_progreso_leccion_usuario_id", "progreso_leccion", ["usuario_id"])
    op.create_index("ix_progreso_leccion_leccion_id", "progreso_leccion", ["leccion_id"])

    op.create_table(
        "streaks",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id"), nullable=False),
        sa.Column("current_streak", sa.Integer(), server_default="0", nullable=False),
        sa.Column("longest_streak", sa.Integer(), server_default="0", nullable=False),
        sa.Column("last_event_date", sa.Date(), nullable=True),
        sa.Column("timezone", sa.String(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
    )
    op.create_index("ix_streaks_usuario_id", "streaks", ["usuario_id"])


def downgrade() -> None:
    op.drop_index("ix_streaks_usuario_id", table_name="streaks")
    op.drop_table("streaks")

    op.drop_index("ix_progreso_leccion_leccion_id", table_name="progreso_leccion")
    op.drop_index("ix_progreso_leccion_usuario_id", table_name="progreso_leccion")
    op.drop_table("progreso_leccion")

    op.drop_index("ix_gasto_user_cat", table_name="gastos")
    op.drop_index("ix_gasto_user_fecha", table_name="gastos")
    op.drop_table("gastos")
