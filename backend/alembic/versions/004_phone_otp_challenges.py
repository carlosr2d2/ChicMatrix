"""Phone OTP challenges table

Revision ID: 004
Revises: 003
Create Date: 2026-07-09
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "phone_otp_challenges",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("otp_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_phone_otp_challenges_otp_hash"),
        "phone_otp_challenges",
        ["otp_hash"],
        unique=False,
    )
    op.create_index(
        op.f("ix_phone_otp_challenges_user_id"),
        "phone_otp_challenges",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_phone_otp_challenges_user_id"), table_name="phone_otp_challenges")
    op.drop_index(op.f("ix_phone_otp_challenges_otp_hash"), table_name="phone_otp_challenges")
    op.drop_table("phone_otp_challenges")
