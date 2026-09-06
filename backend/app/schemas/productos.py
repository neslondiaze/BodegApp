"""Pydantic schemas for the products API (M-02, F1-01).

Field names are in Spanish, consistent with the domain and the
integration contract (§3.4). Validation rules from the delegation:
sku unique per tenant (BD constraint), non-negative stock, decimal
prices. proveedor_id is accepted but NOT validated against the
providers table — the provider CRUD is F1-02; for now the FK just
persists the future relation (or stays null).
"""

import enum
import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class UnidadMedidaEnum(str, enum.Enum):
    unidad = "unidad"
    kg = "kg"
    litro = "litro"
    metro = "metro"
    paquete = "paquete"
    caja = "caja"


def _check_no_negativo(value: int) -> int:
    if value < 0:
        raise ValueError("El stock no puede ser negativo.")
    return value


class ProductoCreate(BaseModel):
    """Request body for POST /api/v1/productos."""

    nombre: str = Field(min_length=1, max_length=255)
    sku: str = Field(min_length=1, max_length=100)
    precio: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    stock_actual: int = Field(default=0, ge=0)
    stock_minimo: int = Field(default=0, ge=0)
    proveedor_id: uuid.UUID | None = None
    unidad_medida: UnidadMedidaEnum = UnidadMedidaEnum.unidad

    @field_validator("nombre", "sku")
    @classmethod
    def _strip(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("No puede estar vacío.")
        return v

    @field_validator("stock_actual", "stock_minimo")
    @classmethod
    def _no_negativo(cls, v: int) -> int:
        return _check_no_negativo(v)


class ProductoUpdate(BaseModel):
    """Request body for PUT /api/v1/productos/{id}.

    PUT semantics (full replace, mirroring F1-03): every field in the
    request overwrites the stored value; a concurrent update race on
    sku is fenced by uq_producto_tenant_sku.
    """

    nombre: str = Field(min_length=1, max_length=255)
    sku: str = Field(min_length=1, max_length=100)
    precio: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    stock_actual: int = Field(ge=0)
    stock_minimo: int = Field(ge=0)
    proveedor_id: uuid.UUID | None = None
    unidad_medida: UnidadMedidaEnum

    @field_validator("nombre", "sku")
    @classmethod
    def _strip(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("No puede estar vacío.")
        return v

    @field_validator("stock_actual", "stock_minimo")
    @classmethod
    def _no_negativo(cls, v: int) -> int:
        return _check_no_negativo(v)


class ProductoResponse(BaseModel):
    """Response shape for the producto resource.

    validation_alias is not needed: the ORM columns are already in
    Spanish (contract §3.4), matching the API names 1:1.
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    nombre: str
    sku: str
    precio: Decimal
    stock_actual: int
    stock_minimo: int
    proveedor_id: uuid.UUID | None
    unidad_medida: UnidadMedidaEnum
    creado: datetime = Field(validation_alias="created_at")
    actualizado: datetime = Field(validation_alias="updated_at")


class ProductoListResponse(BaseModel):
    """Paginated list envelope for GET /api/v1/productos."""

    items: list[ProductoResponse]
    total: int
