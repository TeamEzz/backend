"""merge lecciones and soft delete heads

Revision ID: f0e1d2c3b4a5
Revises: b2e7f1d4c9a0, d5e9c3a7f1b2
Create Date: 2026-06-24 00:00:00.000000

"""
from typing import Sequence, Union

revision: str = "f0e1d2c3b4a5"
down_revision: Union[str, Sequence[str], None] = ("b2e7f1d4c9a0", "d5e9c3a7f1b2")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
