"""Add products.image_source_url for remote originals behind local media cache

Revision ID: 008
Revises: 007
Create Date: 2026-08-13
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "008"
down_revision: Union[str, None] = "007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("products", sa.Column("image_source_url", sa.String(length=1024), nullable=True))


def downgrade() -> None:
    op.drop_column("products", "image_source_url")
