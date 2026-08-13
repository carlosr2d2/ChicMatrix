"""Style tags taxonomy and product_url

Revision ID: 006
Revises: 005
Create Date: 2026-08-12
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("products", sa.Column("product_url", sa.String(length=1024), nullable=True))

    op.create_table(
        "style_tags",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=40), nullable=False),
        sa.Column("label_es", sa.String(length=80), nullable=False),
        sa.Column("active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_style_tags_code", "style_tags", ["code"])

    op.create_table(
        "product_style_tags",
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("model_version", sa.String(length=40), nullable=False),
        sa.Column(
            "classified_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tag_id"], ["style_tags.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("product_id", "tag_id"),
    )
    op.create_index("ix_product_style_tags_tag_id", "product_style_tags", ["tag_id"])


def downgrade() -> None:
    op.drop_index("ix_product_style_tags_tag_id", table_name="product_style_tags")
    op.drop_table("product_style_tags")
    op.drop_index("ix_style_tags_code", table_name="style_tags")
    op.drop_table("style_tags")
    op.drop_column("products", "product_url")
