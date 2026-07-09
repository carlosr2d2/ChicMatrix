"""User auth fields and UUID primary key

Revision ID: 002
Revises: 001
Create Date: 2026-07-09
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("phone", sa.String(length=20), nullable=True))
    op.add_column("users", sa.Column("password_hash", sa.String(length=255), nullable=True))
    op.add_column("users", sa.Column("otp_secret", sa.String(length=64), nullable=True))
    op.add_column("users", sa.Column("social_provider", sa.String(length=20), nullable=True))
    op.add_column("users", sa.Column("social_id", sa.String(length=255), nullable=True))
    op.add_column(
        "users",
        sa.Column("verified", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )
    op.add_column(
        "users",
        sa.Column("consent_given_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column("users", sa.Column("consent_version", sa.String(length=20), nullable=True))

    op.alter_column("users", "email", existing_type=sa.String(length=255), nullable=True)
    op.alter_column("users", "name", existing_type=sa.String(length=120), nullable=True)

    op.create_index(op.f("ix_users_phone"), "users", ["phone"], unique=True)
    op.create_index(
        "ix_users_social_provider_social_id",
        "users",
        ["social_provider", "social_id"],
        unique=True,
        postgresql_where=sa.text("social_provider IS NOT NULL AND social_id IS NOT NULL"),
    )

    op.add_column(
        "users",
        sa.Column(
            "new_id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
    )

    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_constraint("users_pkey", "users", type_="primary")
    op.drop_column("users", "id")
    op.alter_column("users", "new_id", new_column_name="id")
    op.create_primary_key("users_pkey", "users", ["id"])
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    op.execute("UPDATE users SET verified = true WHERE email IS NOT NULL")


def downgrade() -> None:
    op.add_column(
        "users",
        sa.Column("old_id", sa.Integer(), autoincrement=True, nullable=False),
    )
    op.execute(
        """
        UPDATE users SET old_id = sub.rn
        FROM (SELECT id, ROW_NUMBER() OVER (ORDER BY created_at) AS rn FROM users) sub
        WHERE users.id = sub.id
        """
    )

    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_constraint("users_pkey", "users", type_="primary")
    op.drop_column("users", "id")
    op.alter_column("users", "old_id", new_column_name="id")
    op.create_primary_key("users_pkey", "users", ["id"])
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    op.drop_index("ix_users_social_provider_social_id", table_name="users")
    op.drop_index(op.f("ix_users_phone"), table_name="users")

    op.alter_column("users", "name", existing_type=sa.String(length=120), nullable=False)
    op.alter_column("users", "email", existing_type=sa.String(length=255), nullable=False)

    op.drop_column("users", "consent_version")
    op.drop_column("users", "consent_given_at")
    op.drop_column("users", "verified")
    op.drop_column("users", "social_id")
    op.drop_column("users", "social_provider")
    op.drop_column("users", "otp_secret")
    op.drop_column("users", "password_hash")
    op.drop_column("users", "phone")
