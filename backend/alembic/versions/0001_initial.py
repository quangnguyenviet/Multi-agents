"""initial schema: users and conversations

Revision ID: 0001
Revises:
Create Date: 2026-06-09
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    existing = inspect(bind).get_table_names()

    if "users" not in existing:
        op.create_table(
            "users",
            sa.Column("id",            sa.String(),              nullable=False),
            sa.Column("username",      sa.String(),              nullable=False),
            sa.Column("password_hash", sa.String(),              nullable=False),
            sa.Column("name",          sa.String(),              nullable=False),
            sa.Column("role",          sa.String(),              nullable=False, server_default="user"),
            sa.Column("created_at",    sa.DateTime(timezone=True), server_default=sa.text("now()")),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("username"),
        )

    if "conversations" not in existing:
        op.create_table(
            "conversations",
            sa.Column("id",         sa.String(), nullable=False),
            sa.Column("user_id",    sa.String(), nullable=False),
            sa.Column("title",      sa.String(), nullable=False, server_default=""),
            sa.Column("created_at", sa.Float(),  nullable=False),
            sa.Column("updated_at", sa.Float(),  nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("idx_conv_user", "conversations", ["user_id"])


def downgrade() -> None:
    op.drop_index("idx_conv_user", table_name="conversations")
    op.drop_table("conversations")
    op.drop_table("users")
