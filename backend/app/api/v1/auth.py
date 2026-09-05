"""Auth endpoints (integration contract §2): login, refresh, logout, me."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.api.deps import CurrentUser
from app.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    LogoutResponse,
    MeResponse,
    RefreshRequest,
    RefreshResponse,
    TokenPairResponse,
)
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=TokenPairResponse,
    status_code=status.HTTP_200_OK,
)
async def login(
    payload: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> TokenPairResponse:
    """Issue the dual token pair (work + contractor)."""
    return await auth_service.login(db, payload)


@router.post(
    "/refresh",
    response_model=RefreshResponse,
    status_code=status.HTTP_200_OK,
)
async def refresh(
    payload: RefreshRequest,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> RefreshResponse:
    """Exchange a contractor token for a fresh work token (rotation T3)."""
    return await auth_service.refresh(db, payload.refresh_token)


@router.post(
    "/logout",
    response_model=LogoutResponse,
    status_code=status.HTTP_200_OK,
)
async def logout(
    payload: LogoutRequest,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> LogoutResponse:
    """Revoke the contractor token (contract T6). Idempotent."""
    return await auth_service.logout(db, payload.refresh_token)


@router.get("/me", response_model=MeResponse)
async def me(current_user: CurrentUser) -> MeResponse:
    """Return the caller identity (useful for the frontend session check)."""
    return MeResponse(
        id=current_user.id,
        username=current_user.username,
        full_name=current_user.full_name,
        role=current_user.role,
        tenant_id=current_user.tenant_id,
    )
