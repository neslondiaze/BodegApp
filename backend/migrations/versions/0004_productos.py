"""Products table (M-02, F1-01) with strict tenant isolation

Revision ID: 0004
Revises: 0003
Create Date: 2026-09-05

Creates `proveedores` as a placeholder (id + tenant_id only): the full
provider model is F1-02 (30/09), but productos needs the FK NOW so the
schema is not reworked later. Creates `productos` with FK to tenants
(ondelete CASCADE) and nullable FK to proveedores (ondelete SET NULL).
sku is unique PER TENANT (uq_producto_tenant_sku), never global — two
stores can both sell "HARINA-01". Prices are Numeric(12,2) decimals.
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Placeholder for F1-02: identity columns only, so productos has a
    # real FK target. F1-02 will extend it with the full provider fields.
    op.create_table(
        "proveedores",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "tenant_id",
            sa.Uuid(),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "productos",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "tenant_id",
            sa.Uuid(),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("nombre", sa.String(length=255), nullable=False),
        sa.Column("sku", sa.String(length=100), nullable=False),
        sa.Column("precio", sa.Numeric(12, 2), nullable=False),
        sa.Column("stock_actual", sa.Integer(), nullable=False),
        sa.Column("stock_minimo", sa.Integer(), nullable=False),
        sa.Column(
            "proveedor_id",
            sa.Uuid(),
            sa.ForeignKey("proveedores.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("unidad_medida", sa.String(length=20), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "sku", name="uq_producto_tenant_sku"),
    )


def downgrade() -> None:
    op.drop_table("productos")
    op.drop_table("proveedores")
