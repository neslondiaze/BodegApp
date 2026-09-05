"""Products endpoints (M-02, F1-01): CRUD with strict tenant isolation.

Contract rules: /api/v1 versioning, plural Spanish resource names,
tenant identity from the JWT only (rule T5), uniform error envelope,
404 (not 403) for cross-tenant resources. RBAC provisional matrix
(BT-SR01-02, defined by Cristian): GET lista/detalle → owner/admin/
staff; POST/PUT/DELETE → owner/admin (staff never writes the catalog).
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, require_role
from app.db.session import get_db_session
from app.models import UserRole
from app.schemas.productos import (
    ProductoCreate,
    ProductoListResponse,
    ProductoResponse,
    ProductoUpdate,
)
from app.services import producto_service

router = APIRouter(prefix="/productos", tags=["productos"])

# RBAC provisional (BT-SR01-02). Reader = any authenticated role;
# Writer = owner/admin only — staff does not write the catalog.
ReaderUser = Annotated[
    object, Depends(require_role(UserRole.owner, UserRole.admin, UserRole.staff))
]
WriterUser = Annotated[
    object, Depends(require_role(UserRole.owner, UserRole.admin))
]


@router.get(
    "",
    response_model=ProductoListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_productos(
    current_user: CurrentUser,
    _rbac: ReaderUser,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> ProductoListResponse:
    """List only the caller's tenant products (never another tenant's)."""
    items, total = await producto_service.list_productos(
        db, current_user.tenant_id, limit=limit, offset=offset
    )
    return ProductoListResponse(
        items=[ProductoResponse.model_validate(p) for p in items],
        total=total,
    )


@router.get(
    "/{producto_id}",
    response_model=ProductoResponse,
    status_code=status.HTTP_200_OK,
)
async def get_producto(
    producto_id: uuid.UUID,
    current_user: CurrentUser,
    _rbac: ReaderUser,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> ProductoResponse:
    """Return one product; cross-tenant ids are a uniform 404."""
    producto = await producto_service.get_producto(
        db, current_user.tenant_id, producto_id
    )
    return ProductoResponse.model_validate(producto)


@router.post(
    "",
    response_model=ProductoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_producto(
    payload: ProductoCreate,
    current_user: CurrentUser,
    _rbac: WriterUser,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> ProductoResponse:
    """Create a product in the caller's tenant (owner/admin only)."""
    producto = await producto_service.create_producto(
        db, current_user.tenant_id, payload
    )
    return ProductoResponse.model_validate(producto)


@router.put(
    "/{producto_id}",
    response_model=ProductoResponse,
    status_code=status.HTTP_200_OK,
)
async def update_producto(
    producto_id: uuid.UUID,
    payload: ProductoUpdate,
    current_user: CurrentUser,
    _rbac: WriterUser,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> ProductoResponse:
    """Full replace of the caller's product (owner/admin only).

    404 uniform cross-tenant: another tenant's id never leaks, not even
    its existence.
    """
    producto = await producto_service.update_producto(
        db, current_user.tenant_id, producto_id, payload
    )
    return ProductoResponse.model_validate(producto)


@router.delete(
    "/{producto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_producto(
    producto_id: uuid.UUID,
    current_user: CurrentUser,
    _rbac: WriterUser,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> None:
    """Delete the caller's product (owner/admin only). 204 on success;
    cross-tenant ids are a uniform 404 with no side effects."""
    await producto_service.delete_producto(
        db, current_user.tenant_id, producto_id
    )
