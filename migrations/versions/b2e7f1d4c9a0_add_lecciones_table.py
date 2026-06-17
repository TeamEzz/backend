"""add lecciones table

Revision ID: b2e7f1d4c9a0
Revises: a4d8f2c10b5e
Create Date: 2026-06-17 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "b2e7f1d4c9a0"
down_revision: Union[str, None] = "a4d8f2c10b5e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "lecciones",
        sa.Column("id", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("nivel", sa.Integer(), nullable=False),
        sa.Column("orden", sa.Integer(), nullable=False),
        sa.Column("titulo", sa.String(), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("duracion_minutos", sa.Integer(), nullable=True),
        sa.Column("imagen_portada_key", sa.String(), nullable=True),
        sa.Column("activa", sa.Boolean(), nullable=True, server_default=sa.text("true")),
        sa.Column("contenido", JSONB(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=True, server_default=sa.text("1")),
        sa.Column(
            "creado_en",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "actualizado_en",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_lecciones_nivel", "lecciones", ["nivel"])


def downgrade() -> None:
    op.drop_index("ix_lecciones_nivel", table_name="lecciones")
    op.drop_table("lecciones")
