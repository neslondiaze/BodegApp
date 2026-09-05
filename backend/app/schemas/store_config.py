"""Pydantic schemas for the store configuration API (M-01).

Field names are in Spanish, consistent with the domain and the
integration contract (§3.4). Only `nombre_comercial` is mandatory:
a tenant must be able to save partial configuration and complete it
later; the M-16 ticket printing will validate the presence of fiscal
fields at print time, not at configuration time.
"""

import re
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

# Venezuelan RIF: type letter (V, E, J, P, G) + 7-9 digits + check digit.
# 7-digit bodies are legacy cédulas (E-1234567-8); jurídicas use 8-9
# (J-12345678-9). Stored/returned WITHOUT dashes.
RIF_PATTERN = re.compile(r"^[VEJPG](-?\d{7,9}-?\d)$")

VALID_CURRENCIES = ("VES", "USD")


def normalize_rif(value: str | None) -> str | None:
    """Validate a Venezuelan RIF and return it without dashes."""
    if value is None:
        return None
    if not RIF_PATTERN.match(value.upper().strip()):
        raise ValueError(
            "El RIF debe tener el formato venezolano, por ejemplo J-12345678-9."
        )
    return value.upper().replace("-", "")


class StoreConfigUpdate(BaseModel):
    """Request body for creating or replacing the tenant's store config."""

    nombre_comercial: str = Field(min_length=1, max_length=255)
    rif: str | None = Field(default=None, max_length=20)
    razon_social: str | None = Field(default=None, max_length=255)
    direccion: str | None = Field(default=None, max_length=255)
    direccion_fiscal: str | None = Field(default=None, max_length=255)
    telefono: str | None = Field(default=None, max_length=50)
    moneda: str = Field(default="VES", max_length=3)

    @field_validator("rif")
    @classmethod
    def validate_rif(cls, v: str | None) -> str | None:
        return normalize_rif(v)

    @field_validator("moneda")
    @classmethod
    def validate_moneda(cls, v: str) -> str:
        v = v.upper()
        if v not in VALID_CURRENCIES:
            raise ValueError("La moneda debe ser VES o USD.")
        return v


class StoreConfigResponse(BaseModel):
    """Response shape for the store configuration resource.

    validation_alias maps the Spanish API names to the English ORM
    attribute names (contract §3.4: domain fields in Spanish, code in
    English).
    """

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    nombre_comercial: str = Field(validation_alias="store_name")
    rif: str | None
    razon_social: str | None
    direccion: str | None = Field(validation_alias="address")
    direccion_fiscal: str | None = Field(validation_alias="fiscal_address")
    telefono: str | None = Field(validation_alias="phone")
    moneda: str = Field(validation_alias="currency")
    creado: datetime = Field(validation_alias="created_at")
    actualizado: datetime = Field(validation_alias="updated_at")
