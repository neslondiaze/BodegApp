"""Fiscal fields for store_configs (M-16 Ticket Fiscal readiness)

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-04

Adds nullable fiscal identity columns to store_configs: rif,
razon_social, fiscal_address. Nullable because existing tenants must
keep working without re-seeding; the M-01 API validates format (RIF)
but only store_name is mandatory. Included now so M-16 (Ticket Fiscal)
does not force a schema rework right after the M-01 CRUD ships.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("store_configs", sa.Column("rif", sa.String(length=20), nullable=True))
    op.add_column(
        "store_configs", sa.Column("razon_social", sa.String(length=255), nullable=True)
    )
    op.add_column(
        "store_configs", sa.Column("fiscal_address", sa.String(length=255), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("store_configs", "fiscal_address")
    op.drop_column("store_configs", "razon_social")
    op.drop_column("store_configs", "rif")
