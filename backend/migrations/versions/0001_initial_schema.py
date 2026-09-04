"""Initial schema: tenants, users, store_configs

Revision ID: 0001
Revises:
Create Date: 2026-09-03

Creates the three base tables for the multi-tenant model (F0-03):
- tenants
- users (username unique per tenant via uq_user_tenant_username)
- store_configs (one row per tenant via unique tenant_id)
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.models import UserRole

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tenants",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tenants_slug"), "tenants", ["slug"], unique=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column(
            "role",
            sa.Enum("owner", "admin", "staff", name="userrole", native_enum=False, length=20),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "username", name="uq_user_tenant_username"),
        sa.UniqueConstraint("email", name="uq_user_email"),
    )
    op.create_index(op.f("ix_users_tenant_id"), "users", ["tenant_id"])

    op.create_table(
        "store_configs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("tenant_id", sa.Uuid(), nullable=False),
        sa.Column("store_name", sa.String(length=255), nullable=False),
        sa.Column("address", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", name="uq_store_config_tenant"),
    )


def downgrade() -> None:
    op.drop_table("store_configs")
    op.drop_index(op.f("ix_users_tenant_id"), table_name="users")
    op.drop_table("users")
    op.drop_index(op.f("ix_tenants_slug"), table_name="tenants")
    op.drop_table("tenants")
