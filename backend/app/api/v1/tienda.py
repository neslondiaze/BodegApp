"""Store configuration endpoints (M-01): get / upsert per tenant.

Contract rules: /api/v1 versioning, plural Spanish resource names,
tenant identity from the JWT only (rule T5), uniform error envelope.
PUT uses upsert semantics because each tenant has exactly one config
row — the frontend saves the whole form in a single request.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser
from app.db.session import get_db_session
from app.schemas.store_config import StoreConfigResponse, StoreConfigUpdate
from app.services import store_config_service

router = APIRouter(prefix="/tienda", tags=["tienda"])


@router.get(
    "/configuracion",
    response_model=StoreConfigResponse,
    status_code=status.HTTP_200_OK,
)
async def get_configuracion(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> StoreConfigResponse:
    """Return the caller's tenant store configuration.

    404 RECURSO_NO_ENCONTRADO when the tenant has not saved any
    configuration yet — the frontend uses this to decide between
    "create" and "edit" mode.
    """
    config = await store_config_service.get_store_config(db, current_user.tenant_id)
    return StoreConfigResponse.model_validate(config)


@router.put(
    "/configuracion",
    response_model=StoreConfigResponse,
    status_code=status.HTTP_200_OK,
)
async def put_configuracion(
    payload: StoreConfigUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> StoreConfigResponse:
    """Create or replace the tenant's store configuration.

    Returns 200 both on create and update (idempotent full replace):
    the resource is a per-tenant singleton, so the create/update
    distinction carries no meaning for the client.
    """
    config = await store_config_service.upsert_store_config(
        db, current_user.tenant_id, payload
    )
    return StoreConfigResponse.model_validate(config)
