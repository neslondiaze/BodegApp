"""FastAPI dependencies for authentication and tenant scoping.

get_current_user validates the work (access) token and injects the
authenticated identity — with tenant_id taken from the JWT, never from
request parameters (contract rule T5 / QA B7). This is the base every
Phase 1 business endpoint will use for tenant isolation.

require_role (BT-SR01-02) layers RBAC on top: it returns a dependency
that rejects callers whose role is not in the allowed set with 403
PERMISO_INSUFICIENTE. The provisional matrix (Cristian, F1-01):
reads → owner/admin/staff; catalog writes → owner/admin.
"""

from collections.abc import Callable, Coroutine
from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import PermisoInsuficienteError, TokenAusenteError
from app.core.security import decode_token
from app.db.session import get_db_session
from app.models import UserRole
from app.schemas.auth import AuthenticatedUser
from app.services import auth_service

_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)
    ],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> AuthenticatedUser:
    """Resolve the caller identity from the Bearer work token.

    401 TOKEN_AUSENTE when the header is missing; malformed or invalid
    tokens raise the cataloged ApiError from decode_token.
    """
    if credentials is None:
        raise TokenAusenteError()

    # Expose tenant context for request-scoped logging (never the token).
    try:
        payload = decode_token(credentials.credentials)
        request.state.tenant_id = payload.get("tenant_id")
    except Exception:
        # Let the service layer raise the precise cataloged error.
        request.state.tenant_id = None

    return await auth_service.get_authenticated_user(db, credentials.credentials)


CurrentUser = Annotated[AuthenticatedUser, Depends(get_current_user)]


def require_role(
    *allowed: UserRole,
) -> Callable[..., Coroutine[None, None, AuthenticatedUser]]:
    """Build an endpoint dependency enforcing the allowed roles.

    Usage: `user: Annotated[AuthenticatedUser, Depends(require_role(
    UserRole.owner, UserRole.admin))]`. The role comes from the JWT-
    backed identity, never from the request body.
    """

    async def _checker(
        current_user: CurrentUser,
    ) -> AuthenticatedUser:
        if current_user.role not in allowed:
            raise PermisoInsuficienteError()
        return current_user

    return _checker
