"""Auth request/response schemas (integration contract §2).

Login accepts `username` because that is what the frontend apiClient
sends today (frontend/src/lib/apiClient.ts:98). The value may be a
username OR an email — the service resolves both (see auth service).
Contract doc §2.1 writes "usuario"; aligning the doc field name is a
bilateral change pending with Noris (reported in the delivery notes).
"""

import uuid

from pydantic import BaseModel, ConfigDict, Field

from app.models import UserRole


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=1, max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=1)


class LogoutRequest(BaseModel):
    refresh_token: str = Field(min_length=1)


class TenantInfo(BaseModel):
    id: uuid.UUID
    nombre: str


class TokenPairResponse(BaseModel):
    """Login/refresh success shape (contract §2.1/§2.3).

    access_token: work token (trabajo), ~15 min.
    refresh_token: contractor token (contratante), 7 days.
    """

    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int
    tenant: TenantInfo


class RefreshResponse(BaseModel):
    """Refresh success shape consumed by apiClient.ts:78.

    refresh_token is always present: when rotation is disabled it equals
    the token sent in the request; when enabled it is the new contractor
    token the frontend must replace atomically (contract T3).
    """

    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int


class LogoutResponse(BaseModel):
    mensaje: str


class MeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    full_name: str
    role: UserRole
    tenant_id: uuid.UUID


class AuthenticatedUser(BaseModel):
    """Identity injected by get_current_user into downstream handlers."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    username: str
    full_name: str
    role: UserRole
