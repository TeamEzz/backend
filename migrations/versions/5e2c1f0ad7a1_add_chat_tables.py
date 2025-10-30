"""add chat tables conversaciones and mensajes

Revision ID: 5e2c1f0ad7a1
Revises: 1f9d8b0a3c4e
Create Date: 2025-10-30 06:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5e2c1f0ad7a1"
down_revision: Union[str, Sequence[str], None] = "1f9d8b0a3c4e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "conversaciones",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id"), nullable=False),
        sa.Column("titulo", sa.String(), nullable=True),
        sa.Column("fecha_creacion", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("fecha_ultima_actualizacion", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_conversaciones_usuario_id", "conversaciones", ["usuario_id"])

    op.create_table(
        "mensajes",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("conversacion_id", sa.Integer(), sa.ForeignKey("conversaciones.id", ondelete="CASCADE"), nullable=False),
        sa.Column("remitente", sa.String(), nullable=False),  # 'user' o 'assistant'
        sa.Column("contenido", sa.Text(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_mensajes_conversacion_id", "mensajes", ["conversacion_id"])
    op.create_index("ix_mensajes_conversacion_ts", "mensajes", ["conversacion_id", "timestamp"])


def downgrade() -> None:
    op.drop_index("ix_mensajes_conversacion_ts", table_name="mensajes")
    op.drop_index("ix_mensajes_conversacion_id", table_name="mensajes")
    op.drop_table("mensajes")

    op.drop_index("ix_conversaciones_usuario_id", table_name="conversaciones")
    op.drop_table("conversaciones")

