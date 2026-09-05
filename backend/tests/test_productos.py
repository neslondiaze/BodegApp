"""Products API tests (M-02, F1-01).

Covers: CRUD lifecycle, tenant isolation (the 4 multi-row scenarios
SR-01 demands: list count, GET/PUT/DELETE cross-tenant → 404 with no
side effects), RBAC provisional matrix (BT-SR01-02: staff reads but
never writes), auth guard, and validations (sku unique per tenant,
non-negative stock, decimal prices, empty names).
"""

import uuid

import pytest
from httpx import AsyncClient

from app.models import Tenant
from tests.conftest import (
    auth_headers,
    login_as,
    make_tenant,
    make_user,
    producto_payload,
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


async def seed_staff_user(db_session) -> None:
    """A staff user in the FIRST tenant (username `cajero`)."""
    from sqlalchemy import select

    from app.models import UserRole

    tenant = (
        (await db_session.execute(select(Tenant).limit(1))).scalars().first()
    )
    staff = make_user(
        tenant,
        username="cajero",
        email="cajero@bodegapp.dev",
        role=UserRole.staff,
    )
    db_session.add(staff)
    await db_session.flush()


async def create_product(client: AsyncClient, tokens: dict, **overrides) -> dict:
    response = await client.post(
        "/api/v1/productos",
        json=producto_payload(**overrides),
        headers=auth_headers(tokens),
    )
    assert response.status_code == 201, response.text
    return response.json()


class TestAuthGuard:
    async def test_list_without_token_is_401(self, app_client):
        response = await app_client.get("/api/v1/productos")
        assert response.status_code == 401
        assert response.json()["error"]["codigo"] == "TOKEN_AUSENTE"

    async def test_post_without_token_is_401(self, app_client):
        response = await app_client.post(
            "/api/v1/productos", json=producto_payload()
        )
        assert response.status_code == 401
        assert response.json()["error"]["codigo"] == "TOKEN_AUSENTE"

    async def test_put_without_token_is_401(self, app_client):
        response = await app_client.put(
            f"/api/v1/productos/{uuid.uuid4()}", json=producto_payload()
        )
        assert response.status_code == 401

    async def test_delete_without_token_is_401(self, app_client):
        response = await app_client.delete(f"/api/v1/productos/{uuid.uuid4()}")
        assert response.status_code == 401


class TestCreateProducto:
    async def test_create_returns_201(self, seeded_client):
        tokens = await login_as(seeded_client, "admin")
        data = await create_product(seeded_client, tokens)
        assert uuid.UUID(data["id"])
        assert data["nombre"] == "Harina de Maíz"
        assert data["sku"] == "HARINA-01"
        assert data["precio"] == "25.50"
        assert data["stock_actual"] == 100
        assert data["stock_minimo"] == 10
        assert data["unidad_medida"] == "kg"
        assert data["proveedor_id"] is None
        assert data["creado"] and data["actualizado"]

    async def test_create_defaults(self, seeded_client):
        tokens = await login_as(seeded_client, "admin")
        payload = producto_payload()
        payload.pop("unidad_medida")
        response = await seeded_client.post(
            "/api/v1/productos", json=payload, headers=auth_headers(tokens)
        )
        assert response.status_code == 201
        assert response.json()["unidad_medida"] == "unidad"

    async def test_duplicate_sku_same_tenant_is_422(self, seeded_client):
        tokens = await login_as(seeded_client, "admin")
        first = await create_product(seeded_client, tokens)
        response = await seeded_client.post(
            "/api/v1/productos",
            json=producto_payload(sku=first["sku"]),
            headers=auth_headers(tokens),
        )
        assert response.status_code == 422
        assert response.json()["error"]["codigo"] == "VALIDACION_ERROR"

    async def test_negative_stock_is_422(self, seeded_client):
        tokens = await login_as(seeded_client, "admin")
        response = await seeded_client.post(
            "/api/v1/productos",
            json=producto_payload(stock_actual=-1),
            headers=auth_headers(tokens),
        )
        assert response.status_code == 422
        assert response.json()["error"]["codigo"] == "VALIDACION_ERROR"

    async def test_negative_precio_is_422(self, seeded_client):
        tokens = await login_as(seeded_client, "admin")
        response = await seeded_client.post(
            "/api/v1/productos",
            json=producto_payload(precio="-5.00"),
            headers=auth_headers(tokens),
        )
        assert response.status_code == 422

    async def test_decimal_precio_roundtrip(self, seeded_client):
        tokens = await login_as(seeded_client, "admin")
        data = await create_product(seeded_client, tokens, precio="1234.99")
        assert data["precio"] == "1234.99"

    async def test_empty_nombre_is_422(self, seeded_client):
        tokens = await login_as(seeded_client, "admin")
        response = await seeded_client.post(
            "/api/v1/productos",
            json=producto_payload(nombre="   "),
            headers=auth_headers(tokens),
        )
        assert response.status_code == 422

    async def test_sku_unique_across_tenants_allowed(
        self, seeded_client, db_session
    ):
        """Two tenants can both use sku HARINA-01 (unique PER tenant)."""
        await seed_second_tenant(db_session)
        tokens_a = await login_as(seeded_client, "admin")
        prod_a = await create_product(seeded_client, tokens_a)

        tokens_b = await login_as(seeded_client, "otro_admin")
        prod_b = await create_product(seeded_client, tokens_b)  # same sku!

        assert prod_a["id"] != prod_b["id"]
        assert prod_a["tenant_id"] != prod_b["tenant_id"]


class TestGetProducto:
    async def test_get_detail_after_create(self, seeded_client):
        tokens = await login_as(seeded_client, "admin")
        created = await create_product(seeded_client, tokens)
        response = await seeded_client.get(
            f"/api/v1/productos/{created['id']}", headers=auth_headers(tokens)
        )
        assert response.status_code == 200
        assert response.json()["sku"] == "HARINA-01"

    async def test_get_unknown_id_is_404(self, seeded_client):
        tokens = await login_as(seeded_client, "admin")
        response = await seeded_client.get(
            f"/api/v1/productos/{uuid.uuid4()}", headers=auth_headers(tokens)
        )
        assert response.status_code == 404
        assert response.json()["error"]["codigo"] == "RECURSO_NO_ENCONTRADO"

    async def test_get_malformed_id_is_422(self, seeded_client):
        tokens = await login_as(seeded_client, "admin")
        response = await seeded_client.get(
            "/api/v1/productos/no-es-un-uuid", headers=auth_headers(tokens)
        )
        assert response.status_code == 422


class TestListProducto:
    async def test_list_returns_only_own_products(self, seeded_client):
        tokens = await login_as(seeded_client, "admin")
        await create_product(seeded_client, tokens, sku="A-1")
        await create_product(seeded_client, tokens, sku="A-2")

        response = await seeded_client.get(
            "/api/v1/productos", headers=auth_headers(tokens)
        )
        assert response.status_code == 200
        body = response.json()
        assert body["total"] == 2
        assert len(body["items"]) == 2
        assert {p["sku"] for p in body["items"]} == {"A-1", "A-2"}

    async def test_list_empty_returns_empty(self, seeded_client):
        tokens = await login_as(seeded_client, "admin")
        response = await seeded_client.get(
            "/api/v1/productos", headers=auth_headers(tokens)
        )
        assert response.status_code == 200
        assert response.json() == {"items": [], "total": 0}


class TestUpdateProducto:
    async def test_put_replaces_fields(self, seeded_client):
        tokens = await login_as(seeded_client, "admin")
        created = await create_product(seeded_client, tokens)
        response = await seeded_client.put(
            f"/api/v1/productos/{created['id']}",
            json=producto_payload(
                nombre="Harina Premium",
                precio="30.75",
                stock_actual=55,
                sku="HARINA-02",
            ),
            headers=auth_headers(tokens),
        )
        assert response.status_code == 200
        data = response.json()
        assert data["nombre"] == "Harina Premium"
        assert data["precio"] == "30.75"
        assert data["stock_actual"] == 55
        assert data["sku"] == "HARINA-02"
        assert data["id"] == created["id"]

    async def test_put_to_existing_sku_is_422(self, seeded_client):
        tokens = await login_as(seeded_client, "admin")
        await create_product(seeded_client, tokens, sku="A-1")
        target = await create_product(seeded_client, tokens, sku="A-2")
        response = await seeded_client.put(
            f"/api/v1/productos/{target['id']}",
            json=producto_payload(sku="A-1"),
            headers=auth_headers(tokens),
        )
        assert response.status_code == 422
        assert response.json()["error"]["codigo"] == "VALIDACION_ERROR"

    async def test_put_unknown_id_is_404(self, seeded_client):
        tokens = await login_as(seeded_client, "admin")
        response = await seeded_client.put(
            f"/api/v1/productos/{uuid.uuid4()}",
            json=producto_payload(),
            headers=auth_headers(tokens),
        )
        assert response.status_code == 404


class TestDeleteProducto:
    async def test_delete_returns_204_then_404(self, seeded_client):
        tokens = await login_as(seeded_client, "admin")
        created = await create_product(seeded_client, tokens)
        response = await seeded_client.delete(
            f"/api/v1/productos/{created['id']}", headers=auth_headers(tokens)
        )
        assert response.status_code == 204
        gone = await seeded_client.get(
            f"/api/v1/productos/{created['id']}", headers=auth_headers(tokens)
        )
        assert gone.status_code == 404

    async def test_delete_unknown_id_is_404(self, seeded_client):
        tokens = await login_as(seeded_client, "admin")
        response = await seeded_client.delete(
            f"/api/v1/productos/{uuid.uuid4()}", headers=auth_headers(tokens)
        )
        assert response.status_code == 404


class TestTenantIsolation:
    """The 4 multi-row scenarios demanded by SR-01 (Lead_Blue)."""

    async def _seed_two_tenants_with_products(self, seeded_client, db_session):
        await seed_second_tenant(db_session)
        tokens_a = await login_as(seeded_client, "admin")
        prod_a = await create_product(seeded_client, tokens_a, sku="A-1")
        prod_a2 = await create_product(seeded_client, tokens_a, sku="A-2")
        tokens_b = await login_as(seeded_client, "otro_admin")
        prod_b = await create_product(seeded_client, tokens_b, sku="B-1")
        return tokens_a, tokens_b, prod_a, prod_a2, prod_b

    async def test_tenant_b_lists_only_own_products(
        self, seeded_client, db_session
    ):
        """Scenario 1 (SR-01): B lists and sees ONLY its own — count check."""
        _, tokens_b, _, _, _ = await self._seed_two_tenants_with_products(
            seeded_client, db_session
        )
        response = await seeded_client.get(
            "/api/v1/productos", headers=auth_headers(tokens_b)
        )
        assert response.status_code == 200
        body = response.json()
        assert body["total"] == 1
        assert [p["sku"] for p in body["items"]] == ["B-1"]

    async def test_tenant_b_get_of_a_id_is_404(
        self, seeded_client, db_session
    ):
        """Scenario 2 (SR-01): B GET /{id_de_A} → 404."""
        _, tokens_b, prod_a, _, _ = await self._seed_two_tenants_with_products(
            seeded_client, db_session
        )
        response = await seeded_client.get(
            f"/api/v1/productos/{prod_a['id']}", headers=auth_headers(tokens_b)
        )
        assert response.status_code == 404
        assert response.json()["error"]["codigo"] == "RECURSO_NO_ENCONTRADO"

    async def test_tenant_b_put_of_a_id_is_404_no_effects(
        self, seeded_client, db_session
    ):
        """Scenario 3 (SR-01): B PUT /{id_de_A} → 404, row intact."""
        tokens_a, tokens_b, prod_a, _, _ = (
            await self._seed_two_tenants_with_products(seeded_client, db_session)
        )
        response = await seeded_client.put(
            f"/api/v1/productos/{prod_a['id']}",
            json=producto_payload(nombre="Hackeado", sku="HACK-1"),
            headers=auth_headers(tokens_b),
        )
        assert response.status_code == 404

        check = await seeded_client.get(
            f"/api/v1/productos/{prod_a['id']}", headers=auth_headers(tokens_a)
        )
        assert check.status_code == 200
        assert check.json()["nombre"] == "Harina de Maíz"
        assert check.json()["sku"] == "A-1"

    async def test_tenant_b_delete_of_a_id_is_404_row_intact(
        self, seeded_client, db_session
    ):
        """Scenario 4 (SR-01): B DELETE /{id_de_A} → 404, A's row intact."""
        tokens_a, tokens_b, prod_a, _, _ = (
            await self._seed_two_tenants_with_products(seeded_client, db_session)
        )
        response = await seeded_client.delete(
            f"/api/v1/productos/{prod_a['id']}", headers=auth_headers(tokens_b)
        )
        assert response.status_code == 404

        check = await seeded_client.get(
            f"/api/v1/productos/{prod_a['id']}", headers=auth_headers(tokens_a)
        )
        assert check.status_code == 200
        assert check.json()["sku"] == "A-1"

        list_a = await seeded_client.get(
            "/api/v1/productos", headers=auth_headers(tokens_a)
        )
        assert list_a.json()["total"] == 2  # both A rows still there
        assert {p["sku"] for p in list_a.json()["items"]} == {"A-1", "A-2"}

    async def test_tenant_id_never_taken_from_body(
        self, seeded_client, db_session
    ):
        """Rule T5: tenant context comes from the JWT only — a foreign
        tenant_id in the body cannot redirect the write."""
        await seed_second_tenant(db_session)
        tokens_a = await login_as(seeded_client, "admin")
        tokens_b = await login_as(seeded_client, "otro_admin")
        tenant_a_id = tokens_a["tenant"]["id"]

        response = await seeded_client.post(
            "/api/v1/productos",
            json={**producto_payload(), "tenant_id": tenant_a_id},
            headers=auth_headers(tokens_b),
        )
        assert response.status_code == 201
        assert response.json()["tenant_id"] == tokens_b["tenant"]["id"]


class TestRBAC:
    """Provisional matrix (BT-SR01-02): staff reads, never writes."""

    async def test_staff_can_list(self, seeded_client, db_session):
        await seed_staff_user(db_session)
        tokens = await login_as(seeded_client, "cajero")
        response = await seeded_client.get(
            "/api/v1/productos", headers=auth_headers(tokens)
        )
        assert response.status_code == 200

    async def test_staff_can_get_detail(self, seeded_client, db_session):
        owner_tokens = await login_as(seeded_client, "admin")
        created = await create_product(seeded_client, owner_tokens)
        await seed_staff_user(db_session)
        staff_tokens = await login_as(seeded_client, "cajero")
        response = await seeded_client.get(
            f"/api/v1/productos/{created['id']}",
            headers=auth_headers(staff_tokens),
        )
        assert response.status_code == 200

    async def test_staff_cannot_create(self, seeded_client, db_session):
        await seed_staff_user(db_session)
        tokens = await login_as(seeded_client, "cajero")
        response = await seeded_client.post(
            "/api/v1/productos",
            json=producto_payload(),
            headers=auth_headers(tokens),
        )
        assert response.status_code == 403
        assert response.json()["error"]["codigo"] == "PERMISO_INSUFICIENTE"

    async def test_staff_cannot_update(self, seeded_client, db_session):
        owner_tokens = await login_as(seeded_client, "admin")
        created = await create_product(seeded_client, owner_tokens)
        await seed_staff_user(db_session)
        staff_tokens = await login_as(seeded_client, "cajero")
        response = await seeded_client.put(
            f"/api/v1/productos/{created['id']}",
            json=producto_payload(),
            headers=auth_headers(staff_tokens),
        )
        assert response.status_code == 403

    async def test_staff_cannot_delete(self, seeded_client, db_session):
        owner_tokens = await login_as(seeded_client, "admin")
        created = await create_product(seeded_client, owner_tokens)
        await seed_staff_user(db_session)
        staff_tokens = await login_as(seeded_client, "cajero")
        response = await seeded_client.delete(
            f"/api/v1/productos/{created['id']}",
            headers=auth_headers(staff_tokens),
        )
        assert response.status_code == 403
        # The row was never touched.
        check = await seeded_client.get(
            f"/api/v1/productos/{created['id']}",
            headers=auth_headers(owner_tokens),
        )
        assert check.status_code == 200

    async def test_admin_role_can_write(self, seeded_client, db_session):
        """admin (not just owner) is a writer per the matrix."""
        from sqlalchemy import select

        from app.models import UserRole

        tenant = (
            (await db_session.execute(select(Tenant).limit(1)))
            .scalars()
            .first()
        )
        admin = make_user(
            tenant,
            username="encargado",
            email="encargado@bodegapp.dev",
            role=UserRole.admin,
        )
        db_session.add(admin)
        await db_session.flush()

        tokens = await login_as(seeded_client, "encargado")
        response = await seeded_client.post(
            "/api/v1/productos",
            json=producto_payload(),
            headers=auth_headers(tokens),
        )
        assert response.status_code == 201


class TestServiceLayer:
    """Direct service calls — the isolation fence itself."""

    async def test_get_scoped_raises_404_cross_tenant(
        self, app_client, db_session
    ):
        from app.core.exceptions import RecursoNoEncontradoError
        from app.services import producto_service

        tenant = make_tenant(name="Bodega Sola", slug="bodega-sola")
        db_session.add(tenant)
        await db_session.flush()

        with pytest.raises(RecursoNoEncontradoError):
            await producto_service.get_producto(
                db_session, tenant.id, uuid.uuid4()
            )

    async def test_create_then_get_roundtrip(self, app_client, db_session):
        from app.schemas.productos import ProductoCreate
        from app.services import producto_service

        tenant = make_tenant(name="Bodega Roundtrip", slug="roundtrip-p")
        db_session.add(tenant)
        await db_session.flush()

        saved = await producto_service.create_producto(
            db_session, tenant.id, ProductoCreate(**producto_payload())
        )
        loaded = await producto_service.get_producto(
            db_session, tenant.id, saved.id
        )
        assert loaded.id == saved.id
        assert loaded.sku == "HARINA-01"
        assert str(loaded.precio) == "25.50"
