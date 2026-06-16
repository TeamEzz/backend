"""add soft delete + anonymization fields to usuarios

Revision ID: d5e9c3a7f1b2
Revises: a4d8f2c10b5e
Create Date: 2026-06-15 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d5e9c3a7f1b2"
down_revision: Union[str, Sequence[str], None] = "a4d8f2c10b5e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("usuarios", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column(
        "usuarios",
        sa.Column("anonymized", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )


def downgrade() -> None:
    op.drop_column("usuarios", "anonymized")
    op.drop_column("usuarios", "deleted_at")
