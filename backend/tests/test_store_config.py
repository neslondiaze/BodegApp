"""Store configuration API tests (M-01, F1-03).

Covers: CRUD lifecycle (get/upsert singleton), tenant isolation
(tenant A never reads or writes tenant B's config), auth guard
(401 without token), RIF/currency validation, partial-save
semantics (only nombre_comercial mandatory), fiscal fields needed
by M-16 Ticket Fiscal, and updated_at changing on edit.
"""

import time
import uuid

import pytest
from httpx import AsyncClient

from app.models import Tenant
from tests.conftest import (
    PASSWORD,
    auth_headers,
    login_as,
    make_tenant,
    make_user,
    tienda_payload,
)


async def seed_second_tenant(db_session) -> Tenant:
    """A second tenant with its own owner (username `otro_admin`)."""
    other = make_tenant(name="Bodega La Esquina", slug="bodega-esquina")
    db_session.add(other)
    await db_session.flush()
    owner = make_user(other, username="otro_admin", email="otro@esquina.dev")
    db_session.add(owner)
    await db_session.flush()
    return other


class TestAuthGuard:
    async def test_get_without_token_is_401(self, app_client):
        response = await app_client.get("/api/v1/tienda/configuracion")
        assert response.status_code == 401
        assert response.json()["error"]["codigo"] == "TOKEN_AUSENTE"

    async def test_put_without_token_is_401(self, app_client):
        response = await app_client.put(
            "/api/v1/tienda/configuracion", json=tienda_payload()
        )
        assert response.status_code == 401
        assert response.json()["error"]["codigo"] == "TOKEN_AUSENTE"


class TestGetConfiguracion:
    async def test_get_before_create_is_404(self, seeded_client):
        tokens = await login_as(seeded_client, "admin")
        response = await seeded_client.get(
            "/api/v1/tienda/configuracion", headers=auth_headers(tokens)
        )
        assert response.status_code == 404
        body = response.json()["error"]
        assert body["codigo"] == "RECURSO_NO_ENCONTRADO"

    async def test_get_returns_saved_config(self, seeded_client):
        tokens = await login_as(seeded_client, "admin")
        saved = await seeded_client.put(
            "/api/v1/tienda/configuracion",
            json=tienda_payload(),
            headers=auth_headers(tokens),
        )
        assert saved.status_code == 200, saved.text

        response = await seeded_client.get(
            "/api/v1/tienda/configuracion", headers=auth_headers(tokens)
        )
        assert response.status_code == 200
        data = response.json()
        assert data["nombre_comercial"] == "Bodega Central C.A."
        assert data["rif"] == "J123456789"  # normalized, no dashes
        assert data["moneda"] == "VES"
        assert data["tenant_id"] == saved.json()["tenant_id"]
        uuid.UUID(data["id"])
        assert data["creado"] and data["actualizado"]


class TestUpsertConfiguracion:
    async def test_put_creates_config(self, seeded_client):
        tokens = await login_as(seeded_client, "admin")
        response = await seeded_client.put(
            "/api/v1/tienda/configuracion",
            json=tienda_payload(),
            headers=auth_headers(tokens),
        )
        assert response.status_code == 200
        data = response.json()
        assert data["nombre_comercial"] == "Bodega Central C.A."
        assert data["razon_social"] == "Bodega Central Compañía Anónima"
        assert data["direccion_fiscal"] == "Av. Principal, Local 4, Caracas"
        assert data["telefono"] == "0212-5551234"

    async def test_put_replaces_config(self, seeded_client):
        tokens = await login_as(seeded_client, "admin")
        first = await seeded_client.put(
            "/api/v1/tienda/configuracion",
            json=tienda_payload(),
            headers=auth_headers(tokens),
        )
        assert first.status_code == 200

        # PUT replaces: the second request genuinely omits telefono
        # (the helper would otherwise inject the default value).
        payload = tienda_payload(
            nombre_comercial="Bodega Central Renombrada",
            direccion="Calles 8 y 9, Valencia",
        )
        payload.pop("telefono")
        response = await seeded_client.put(
            "/api/v1/tienda/configuracion",
            json=payload,
            headers=auth_headers(tokens),
        )
        assert response.status_code == 200
        data = response.json()
        assert data["nombre_comercial"] == "Bodega Central Renombrada"
        assert data["direccion"] == "Calles 8 y 9, Valencia"
        # PUT replaces: omitted optional fields are cleared.
        assert data["telefono"] is None
        assert data["id"] == first.json()["id"]  # singleton, not a new row

    async def test_put_minimal_only_nombre(self, seeded_client):
        """Only nombre_comercial is mandatory (progressive configuration)."""
        tokens = await login_as(seeded_client, "admin")
        response = await seeded_client.put(
            "/api/v1/tienda/configuracion",
            json={"nombre_comercial": "Kiosco Doña María"},
            headers=auth_headers(tokens),
        )
        assert response.status_code == 200
        data = response.json()
        assert data["rif"] is None
        assert data["moneda"] == "VES"  # default

    async def test_put_updates_actualizado(self, seeded_client):
        tokens = await login_as(seeded_client, "admin")
        first = (
            await seeded_client.put(
                "/api/v1/tienda/configuracion",
                json=tienda_payload(),
                headers=auth_headers(tokens),
            )
        ).json()
        # SQLite CURRENT_TIMESTAMP (updated_at source) has 1-second
        # resolution, so two saves within the same second are
        # indistinguishable by timestamp; sleep past the boundary.
        time.sleep(1.1)
        second = (
            await seeded_client.put(
                "/api/v1/tienda/configuracion",
                json=tienda_payload(telefono="0414-5559999"),
                headers=auth_headers(tokens),
            )
        ).json()
        assert second["creado"] == first["creado"]
        assert second["actualizado"] > first["actualizado"]


class TestValidation:
    async def test_invalid_rif_is_422(self, seeded_client):
        tokens = await login_as(seeded_client, "admin")
        response = await seeded_client.put(
            "/api/v1/tienda/configuracion",
            json=tienda_payload(rif="12345678"),
            headers=auth_headers(tokens),
        )
        assert response.status_code == 422
        body = response.json()["error"]
        assert body["codigo"] == "VALIDACION_ERROR"
        fields = {d["campo"] for d in body["detalles"]}
        assert any(f.endswith("rif") for f in fields)

    @pytest.mark.parametrize(
        "rif",
        [
            "J-12345678-9",   # canonical with dashes
            "j-12345678-9",   # lowercase → normalized
            "J123456789",     # compact
            "V-12345678-9",   # natural person
            "E-1234567-8",    # 7-digit body also accepted (old format)
        ],
    )
    async def test_valid_rif_formats(self, seeded_client, rif):
        tokens = await login_as(seeded_client, "admin")
        response = await seeded_client.put(
            "/api/v1/tienda/configuracion",
            json=tienda_payload(rif=rif),
            headers=auth_headers(tokens),
        )
        assert response.status_code == 200, response.text
        assert response.json()["rif"] == rif.upper().replace("-", "")

    async def test_invalid_currency_is_422(self, seeded_client):
        tokens = await login_as(seeded_client, "admin")
        response = await seeded_client.put(
            "/api/v1/tienda/configuracion",
            json=tienda_payload(moneda="EUR"),
            headers=auth_headers(tokens),
        )
        assert response.status_code == 422
        body = response.json()["error"]
        assert body["codigo"] == "VALIDACION_ERROR"

    async def test_usd_currency_accepted(self, seeded_client):
        """Dual-currency stores (VE market) can pick USD as base."""
        tokens = await login_as(seeded_client, "admin")
        response = await seeded_client.put(
            "/api/v1/tienda/configuracion",
            json=tienda_payload(moneda="usd"),
            headers=auth_headers(tokens),
        )
        assert response.status_code == 200
        assert response.json()["moneda"] == "USD"

    async def test_empty_nombre_is_422(self, seeded_client):
        tokens = await login_as(seeded_client, "admin")
        response = await seeded_client.put(
            "/api/v1/tienda/configuracion",
            json={"nombre_comercial": ""},
            headers=auth_headers(tokens),
        )
        assert response.status_code == 422
        assert response.json()["error"]["codigo"] == "VALIDACION_ERROR"

    async def test_malformed_json_is_422_envelope(self, seeded_client):
        """FastAPI body validation errors keep the uniform envelope."""
        tokens = await login_as(seeded_client, "admin")
        response = await seeded_client.put(
            "/api/v1/tienda/configuracion",
            json={"nombre_comercial": 12345},
            headers=auth_headers(tokens),
        )
        assert response.status_code == 422
        assert response.json()["error"]["codigo"] == "VALIDACION_ERROR"


class TestTenantIsolation:
    async def test_tenant_b_cannot_read_tenant_a_config(
        self, seeded_client, db_session
    ):
        await seed_second_tenant(db_session)
        tokens_a = await login_as(seeded_client, "admin")
        put_a = await seeded_client.put(
            "/api/v1/tienda/configuracion",
            json=tienda_payload(),
            headers=auth_headers(tokens_a),
        )
        assert put_a.status_code == 200

        tokens_b = await login_as(seeded_client, "otro_admin")
        response = await seeded_client.get(
            "/api/v1/tienda/configuracion", headers=auth_headers(tokens_b)
        )
        assert response.status_code == 404  # not 403: no existence leak
        assert response.json()["error"]["codigo"] == "RECURSO_NO_ENCONTRADO"

    async def test_tenant_b_put_does_not_touch_tenant_a_config(
        self, seeded_client, db_session
    ):
        """Tenant B saving its own config leaves A's config untouched."""
        await seed_second_tenant(db_session)
        tokens_a = await login_as(seeded_client, "admin")
        config_a = (
            await seeded_client.put(
                "/api/v1/tienda/configuracion",
                json=tienda_payload(),
                headers=auth_headers(tokens_a),
            )
        ).json()

        tokens_b = await login_as(seeded_client, "otro_admin")
        put_b = await seeded_client.put(
            "/api/v1/tienda/configuracion",
            json=tienda_payload(nombre_comercial="La Esquina de Siempre"),
            headers=auth_headers(tokens_b),
        )
        assert put_b.status_code == 200
        config_b = put_b.json()

        # Distinct singletons: different rows, different tenants.
        assert config_b["id"] != config_a["id"]
        assert config_b["tenant_id"] != config_a["tenant_id"]
        assert config_b["nombre_comercial"] == "La Esquina de Siempre"

        get_a = await seeded_client.get(
            "/api/v1/tienda/configuracion", headers=auth_headers(tokens_a)
        )
        assert get_a.json()["nombre_comercial"] == "Bodega Central C.A."

    async def test_no_tenant_param_can_override_scope(self, seeded_client, db_session):
        """Tenant context comes from the JWT only (rule T5): a request
        cannot read another tenant's config even when passing a foreign
        tenant_id in the body/query."""
        await seed_second_tenant(db_session)
        tokens_b = await login_as(seeded_client, "otro_admin")

        tokens_a = await login_as(seeded_client, "admin")
        tenant_a_id = tokens_a["tenant"]["id"]

        response = await seeded_client.put(
            "/api/v1/tienda/configuracion",
            json=tienda_payload(nombre_comercial="Falsificación S.A."),
            headers={**auth_headers(tokens_b), "X-Tenant-Id": tenant_a_id},
        )
        assert response.status_code == 200
        # The write landed in tenant B, never in A.
        assert response.json()["tenant_id"] != tenant_a_id

    async def test_second_put_same_tenant_reuses_row(self, seeded_client):
        tokens = await login_as(seeded_client, "admin")
        first = await seeded_client.put(
            "/api/v1/tienda/configuracion",
            json=tienda_payload(),
            headers=auth_headers(tokens),
        )
        second = await seeded_client.put(
            "/api/v1/tienda/configuracion",
            json=tienda_payload(telefono="0424-0001111"),
            headers=auth_headers(tokens),
        )
        assert first.json()["id"] == second.json()["id"]


class TestServiceLayer:
    """Direct service calls — the isolation fence itself."""

    async def test_get_store_config_scoped_query(self, app_client, db_session):
        from app.core.exceptions import RecursoNoEncontradoError
        from app.services import store_config_service

        tenant = make_tenant(name="Bodega Sin Config", slug="sin-config")
        db_session.add(tenant)
        await db_session.flush()
        with pytest.raises(RecursoNoEncontradoError):
            await store_config_service.get_store_config(db_session, tenant.id)

    async def test_upsert_then_get_roundtrip(self, app_client, db_session):
        from app.schemas.store_config import StoreConfigUpdate
        from app.services import store_config_service

        tenant = make_tenant(name="Bodega Roundtrip", slug="roundtrip")
        db_session.add(tenant)
        await db_session.flush()
        payload = StoreConfigUpdate(**tienda_payload())
        saved = await store_config_service.upsert_store_config(
            db_session, tenant.id, payload
        )
        loaded = await store_config_service.get_store_config(db_session, tenant.id)
        assert loaded.id == saved.id
        assert loaded.store_name == "Bodega Central C.A."
        assert loaded.rif == "J123456789"
