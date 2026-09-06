"""Auth business logic: login, refresh rotation, logout.

Dual-token model (contract §1):
- Work token (access, typ="access"): short-lived, authenticates calls.
- Contractor token (refresh, typ="refresh"): long-lived, ONLY valid at
  /auth/refresh and /auth/logout; stored hashed by jti in refresh_tokens.

Refresh rotation (contract T3) is enabled by default (QA-ST02-01).
The legacy flag BODEGAPP_REFRESH_ROTATION_ENABLED=false remains as an
operational kill-switch. When rotation is enabled, each refresh issues a
new contractor token, revokes the old one, and reuse of a rotated token
revokes the whole descendant chain (theft detection).
"""

import hashlib
import uuid
from datetime import datetime, timedelta, timezone

import sqlalchemy as sa
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import CredencialesInvalidasError, RefreshInvalidoError, TokenInvalidoError
from app.core.security import (
    TOKEN_TYPE_ACCESS,
    TOKEN_TYPE_REFRESH,
    create_access_token,
    create_refresh_token,
    decode_token_of_type,
    verify_password,
)
from app.models import RefreshToken, Tenant, User
from app.schemas.auth import (
    AuthenticatedUser,
    LoginRequest,
    LogoutResponse,
    RefreshResponse,
    TenantInfo,
    TokenPairResponse,
)


def hash_refresh_token_id(jti: str) -> str:
    """SHA-256 of the token jti — the only refresh material persisted."""
    return hashlib.sha256(jti.encode("utf-8")).hexdigest()


async def _find_user_for_login(db: AsyncSession, identifier: str) -> User | None:
    """Login accepts email (globally unique) or username."""
    stmt = (
        select(User)
        .where(
            sa.or_(
                User.email == identifier.lower(),
                User.username == identifier,
            )
        )
        .limit(1)
    )
    result = await db.execute(stmt)
    return result.scalars().first()


async def login(
    db: AsyncSession, credentials: LoginRequest
) -> TokenPairResponse:
    """Authenticate and issue the dual token pair.

    Lookup is by email (globally unique) OR username. A username alone can
    match users across tenants (uq_user_tenant_username); the FIRST match
    with correct password wins. This is safe because password verification
    is the actual gate, and it keeps the flow compatible with the current
    single-field login form. Uniquifying per-tenant usernames for login is
    deferred to the tenant-scoped login flow (F1).
    """
    user = await _find_user_for_login(db, credentials.username)
    tenant: Tenant | None = None
    if user is not None:
        tenant = await db.get(Tenant, user.tenant_id)

    # Uniform failure: never reveal whether the account exists.
    if user is None or tenant is None or not user.is_active or not tenant.is_active:
        raise CredencialesInvalidasError()
    if not verify_password(credentials.password, user.hashed_password):
        raise CredencialesInvalidasError()

    settings = get_settings()
    access_token = create_access_token(
        sub=str(user.id),
        tenant_id=str(user.tenant_id),
        role=user.role.value,
        token_type=TOKEN_TYPE_ACCESS,
    )
    refresh_token, jti = create_refresh_token(
        sub=str(user.id),
        tenant_id=str(user.tenant_id),
        role=user.role.value,
    )
    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=hash_refresh_token_id(jti),
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=settings.refresh_token_days),
        )
    )
    await db.flush()

    return TokenPairResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_minutes * 60,
        tenant=TenantInfo(id=tenant.id, nombre=tenant.name),
    )


async def refresh(
    db: AsyncSession, refresh_token: str
) -> RefreshResponse:
    """Rotate the contractor token and issue a fresh work token.

    Reuse of a rotated token (rotation enabled) revokes the entire chain
    (theft detection, contract T3). Revoked or unknown tokens fail with
    REFRESH_INVALIDO regardless of signature validity.
    """
    settings = get_settings()
    payload = decode_token_of_type(refresh_token, TOKEN_TYPE_REFRESH)
    token_hash = hash_refresh_token_id(payload["jti"])

    stored = (
        await db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
    ).scalars().first()

    if stored is None:
        raise RefreshInvalidoError()
    if stored.revoked_at is not None:
        # Reuse of an already rotated/revoked token → kill the whole chain.
        # The revocation MUST persist even though this request fails:
        # the dependency wrapper rolls back on exception, so commit here
        # first (security side effects are not rolled back with the error).
        await _revoke_chain(db, stored.user_id, chain_root=stored.id)
        await db.commit()
        raise RefreshInvalidoError()
    if stored.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise RefreshInvalidoError()

    user = await db.get(User, uuid.UUID(payload["sub"]))
    tenant = await db.get(Tenant, user.tenant_id) if user is not None else None
    if user is None or tenant is None or not user.is_active or not tenant.is_active:
        raise RefreshInvalidoError()

    new_access = create_access_token(
        sub=payload["sub"],
        tenant_id=payload["tenant_id"],
        role=payload["role"],
        token_type=TOKEN_TYPE_ACCESS,
    )

    if not settings.refresh_rotation_enabled:
        # Rotation disabled (operational kill-switch): the same contractor
        # token is returned. Only for legacy clients that cannot persist a
        # rotated token — the current frontend persists it (QA-F04-03).
        return RefreshResponse(
            access_token=new_access,
            refresh_token=refresh_token,
            expires_in=settings.access_token_minutes * 60,
        )

    new_refresh, new_jti = create_refresh_token(
        sub=payload["sub"],
        tenant_id=payload["tenant_id"],
        role=payload["role"],
    )
    successor = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token_id(new_jti),
        expires_at=datetime.now(timezone.utc)
        + timedelta(days=settings.refresh_token_days),
    )
    db.add(successor)
    await db.flush()
    # Mark the old token rotated: it can no longer be replayed.
    await db.execute(
        update(RefreshToken)
        .where(RefreshToken.id == stored.id)
        .values(revoked_at=datetime.now(timezone.utc), rotated_to_id=successor.id)
    )

    return RefreshResponse(
        access_token=new_access,
        refresh_token=new_refresh,
        expires_in=settings.access_token_minutes * 60,
    )


async def logout(db: AsyncSession, refresh_token: str) -> LogoutResponse:
    """Revoke the contractor token (contract T6). Idempotent: an unknown,
    expired-signature or already-revoked token still returns 200 so logout
    never leaks session state and clients can always clear local state."""
    try:
        payload = decode_token_of_type(refresh_token, TOKEN_TYPE_REFRESH)
    except Exception:
        return LogoutResponse(mensaje="Sesión cerrada")

    token_hash = hash_refresh_token_id(payload["jti"])
    stored = (
        await db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
    ).scalars().first()
    if stored is not None and stored.revoked_at is None:
        await db.execute(
            update(RefreshToken)
            .where(RefreshToken.id == stored.id)
            .values(revoked_at=datetime.now(timezone.utc))
        )

    return LogoutResponse(mensaje="Sesión cerrada")


async def _revoke_chain(db: AsyncSession, user_id: uuid.UUID, chain_root: uuid.UUID) -> None:
    """Revoke every non-revoked token of the user (reuse = theft signal).

    Follows rotated_to_id links from the reused token so the attacker's
    successor tokens die too, then revokes all remaining active tokens
    of the user as a conservative measure.
    """
    now = datetime.now(timezone.utc)
    seen: set[uuid.UUID] = set()
    current_id: uuid.UUID | None = chain_root
    while current_id is not None and current_id not in seen:
        seen.add(current_id)
        row = await db.get(RefreshToken, current_id)
        if row is None:
            break
        await db.execute(
            update(RefreshToken)
            .where(RefreshToken.id == row.id)
            .values(revoked_at=now)
        )
        current_id = row.rotated_to_id
    # Conservative: revoke any other still-active tokens for this user.
    await db.execute(
        update(RefreshToken)
        .where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None),
        )
        .values(revoked_at=now)
    )


async def get_authenticated_user(db: AsyncSession, token: str) -> AuthenticatedUser:
    """Validate a work token and load its identity (tenant from the JWT)."""
    payload = decode_token_of_type(token, TOKEN_TYPE_ACCESS)
    user = await db.get(User, uuid.UUID(payload["sub"]))
    tenant = await db.get(Tenant, user.tenant_id) if user is not None else None
    if user is None or tenant is None or not user.is_active or not tenant.is_active:
        raise TokenInvalidoError()
    return AuthenticatedUser(
        id=user.id,
        tenant_id=user.tenant_id,
        username=user.username,
        full_name=user.full_name,
        role=user.role,
    )
