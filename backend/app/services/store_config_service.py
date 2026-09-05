"""Store configuration service (M-01).

Every operation is scoped by the tenant_id taken from the JWT via
get_current_user (contract rule T5) — never from request parameters.
A tenant reads and writes exactly one configuration row (unique
tenant_id in store_configs), so the API exposes get/upsert semantics
instead of a list.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import RecursoNoEncontradoError
from app.models import StoreConfig
from app.schemas.store_config import StoreConfigUpdate


async def get_store_config(db: AsyncSession, tenant_id) -> StoreConfig:
    """Return the caller's tenant configuration or 404.

    The query filters by tenant_id unconditionally: a config row from
    another tenant is indistinguishable from a missing one (404, no
    cross-tenant existence leak — contract §3.2 note).
    """
    result = await db.execute(
        select(StoreConfig).where(StoreConfig.tenant_id == tenant_id)
    )
    config = result.scalars().first()
    if config is None:
        raise RecursoNoEncontradoError(
            "No existe configuración de tienda para este tenant."
        )
    return config


async def upsert_store_config(
    db: AsyncSession, tenant_id, payload: StoreConfigUpdate
) -> StoreConfig:
    """Create or fully replace the tenant's configuration.

    PUT semantics: every field in the request overwrites the stored
    value (absent optional fields become None). First save creates the
    row; a concurrent create race is fenced by the unique constraint
    on store_configs.tenant_id.
    """
    result = await db.execute(
        select(StoreConfig).where(StoreConfig.tenant_id == tenant_id)
    )
    config = result.scalars().first()
    if config is None:
        config = StoreConfig(tenant_id=tenant_id)
        db.add(config)

    config.store_name = payload.nombre_comercial
    config.rif = payload.rif
    config.razon_social = payload.razon_social
    config.address = payload.direccion
    config.fiscal_address = payload.direccion_fiscal
    config.phone = payload.telefono
    config.currency = payload.moneda
    await db.flush()
    # updated_at is server-generated (onupdate=func.now()) and arrives
    # expired; refresh inside the async context so serializing it later
    # never triggers lazy IO (MissingGreenlet).
    await db.refresh(config)
    return config
