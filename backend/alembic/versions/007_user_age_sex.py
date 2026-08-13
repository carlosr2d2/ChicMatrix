"""Add age and sex to users fashion profile

Revision ID: 007
Revises: 006
Create Date: 2026-08-13
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("age", sa.Integer(), nullable=True))
    op.add_column("users", sa.Column("sex", sa.String(length=32), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "sex")
    op.drop_column("users", "age")
