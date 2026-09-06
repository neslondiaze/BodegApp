"""Products service (M-02, F1-01).

Every operation is scoped by the tenant_id taken from the JWT via
get_current_user (contract rule T5) — never from request parameters.
Multi-row adaptation of the SR-01 pattern (Lead_Blue): detail/update/
delete fetch the row with tenant_id AND id in the SAME where clause →
first() → None ⇒ 404 uniform cross-tenant (no existence leak, no
db.get-then-check). Concurrent create/update races on sku are fenced
by uq_producto_tenant_sku and surface as IntegrityError → handled.
"""

from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import RecursoNoEncontradoError, ValidacionError
from app.models import Producto
from app.schemas.productos import ProductoCreate, ProductoUpdate


async def _get_scoped(
    db: AsyncSession, tenant_id, producto_id
) -> Producto:
    """Fetch a product with tenant + id in the same WHERE: a row from
    another tenant is indistinguishable from a missing one (404)."""
    result = await db.execute(
        select(Producto).where(
            Producto.tenant_id == tenant_id,
            Producto.id == producto_id,
        )
    )
    producto = result.scalars().first()
    if producto is None:
        raise RecursoNoEncontradoError()
    return producto


async def list_productos(
    db: AsyncSession, tenant_id, *, limit: int = 50, offset: int = 0
) -> tuple[list[Producto], int]:
    """List only the caller's tenant products (unconditional filter)."""
    rows = await db.execute(
        select(Producto)
        .where(Producto.tenant_id == tenant_id)
        .order_by(Producto.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    total = await db.execute(
        select(func.count())
        .select_from(Producto)
        .where(Producto.tenant_id == tenant_id)
    )
    return list(rows.scalars().all()), total.scalar_one()


async def get_producto(db: AsyncSession, tenant_id, producto_id) -> Producto:
    return await _get_scoped(db, tenant_id, producto_id)


async def create_producto(
    db: AsyncSession, tenant_id, payload: ProductoCreate
) -> Producto:
    """Create a product in the caller's tenant.

    A concurrent insert of the same sku races past the pre-check and
    is fenced by uq_producto_tenant_sku (BT-SR01-06): the IntegrityError
    surfaces as a 422 VALIDACION_ERROR, never a 500 leak.
    """
    dup = await db.execute(
        select(Producto).where(
            Producto.tenant_id == tenant_id, Producto.sku == payload.sku
        )
    )
    if dup.scalars().first() is not None:
        raise ValidacionError(
            "Ya existe un producto con ese código (sku) en esta tienda."
        )

    producto = Producto(
        tenant_id=tenant_id,
        nombre=payload.nombre,
        sku=payload.sku,
        precio=payload.precio,
        stock_actual=payload.stock_actual,
        stock_minimo=payload.stock_minimo,
        proveedor_id=payload.proveedor_id,
        unidad_medida=payload.unidad_medida,
    )
    db.add(producto)
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise ValidacionError(
            "Ya existe un producto con ese código (sku) en esta tienda."
        )
    await db.refresh(producto)
    return producto


async def update_producto(
    db: AsyncSession, tenant_id, producto_id, payload: ProductoUpdate
) -> Producto:
    """Full replace of the caller's tenant product (PUT semantics).

    The row is fetched with tenant+id in the same where (404 uniform
    cross-tenant); a sku collision from a concurrent update is fenced
    by uq_producto_tenant_sku.
    """
    producto = await _get_scoped(db, tenant_id, producto_id)

    if payload.sku != producto.sku:
        dup = await db.execute(
            select(Producto).where(
                Producto.tenant_id == tenant_id,
                Producto.sku == payload.sku,
                Producto.id != producto.id,
            )
        )
        if dup.scalars().first() is not None:
            raise ValidacionError(
                "Ya existe un producto con ese código (sku) en esta tienda."
            )

    producto.nombre = payload.nombre
    producto.sku = payload.sku
    producto.precio = payload.precio
    producto.stock_actual = payload.stock_actual
    producto.stock_minimo = payload.stock_minimo
    producto.proveedor_id = payload.proveedor_id
    producto.unidad_medida = payload.unidad_medida
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise ValidacionError(
            "Ya existe un producto con ese código (sku) en esta tienda."
        )
    await db.refresh(producto)
    return producto


async def delete_producto(db: AsyncSession, tenant_id, producto_id) -> None:
    """Delete the caller's tenant product; 404 uniform cross-tenant.

    Deletion also uses tenant+id in the same where: a cross-tenant
    delete is a no-op that reports 404, never a leak or a side effect.
    """
    result = await db.execute(
        delete(Producto)
        .where(
            Producto.tenant_id == tenant_id,
            Producto.id == producto_id,
        )
        .returning(Producto.id)
    )
    if result.scalar_one_or_none() is None:
        raise RecursoNoEncontradoError()
