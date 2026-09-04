import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models import UserRole


# ---------------------------------------------------------------------------
# Tenant
# ---------------------------------------------------------------------------

class TenantBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=100, pattern=r"^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")


class TenantCreate(TenantBase):
    pass


class TenantOut(TenantBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    is_active: bool


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------

class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=255)
    role: UserRole = UserRole.staff


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    is_active: bool


# ---------------------------------------------------------------------------
# StoreConfig
# ---------------------------------------------------------------------------

class StoreConfigBase(BaseModel):
    store_name: str = Field(min_length=1, max_length=255)
    address: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=50)
    currency: str = Field(default="VES", min_length=3, max_length=3)


class StoreConfigCreate(StoreConfigBase):
    pass


class StoreConfigUpdate(BaseModel):
    store_name: str | None = Field(default=None, min_length=1, max_length=255)
    address: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=50)
    currency: str | None = Field(default=None, min_length=3, max_length=3)


class StoreConfigOut(StoreConfigBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
