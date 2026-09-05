"""FastAPI dependencies for authentication and tenant scoping.

get_current_user validates the work (access) token and injects the
authenticated identity — with tenant_id taken from the JWT, never from
request parameters (contract rule T5 / QA B7). This is the base every
Phase 1 business endpoint will use for tenant isolation.
"""

from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import TokenAusenteError
from app.core.security import decode_token
from app.db.session import get_db_session
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
