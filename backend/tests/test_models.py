import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models import Tenant, User, UserRole


def _make_user(tenant_id: uuid.UUID, username: str, email: str) -> User:
    return User(
        tenant_id=tenant_id,
        username=username,
        email=email,
        hashed_password="not-a-real-hash",
        full_name="Test User",
        role=UserRole.staff,
    )


class TestTenantModel:
    async def test_create_tenant(self, db_session):
        tenant = Tenant(name="Bodega Central", slug="bodega-central")
        db_session.add(tenant)
        await db_session.flush()

        assert tenant.id is not None
        assert tenant.is_active is True

    async def test_slug_must_be_unique(self, db_session):
        db_session.add(Tenant(name="Bodega Central", slug="bodega-central"))
        await db_session.flush()

        db_session.add(Tenant(name="Otra Bodega", slug="bodega-central"))
        with pytest.raises(IntegrityError):
            await db_session.flush()


class TestUserModel:
    async def test_create_two_users_same_tenant(self, db_session):
        tenant = Tenant(name="Bodega Central", slug="bodega-central")
        db_session.add(tenant)
        await db_session.flush()

        owner = _make_user(tenant.id, "nelson", "nelson@bodegapp.dev")
        owner.role = UserRole.owner
        staff = _make_user(tenant.id, "maria", "maria@bodegapp.dev")
        db_session.add_all([owner, staff])
        await db_session.flush()

        result = await db_session.execute(
            select(User).where(User.tenant_id == tenant.id)
        )
        users = result.scalars().all()
        assert len(users) == 2
        assert {u.username for u in users} == {"nelson", "maria"}
        assert {u.role for u in users} == {UserRole.owner, UserRole.staff}

    async def test_username_unique_within_tenant(self, db_session):
        tenant = Tenant(name="Bodega Central", slug="bodega-central")
        db_session.add(tenant)
        await db_session.flush()

        db_session.add(_make_user(tenant.id, "cajero", "cajero@bodegapp.dev"))
        await db_session.flush()

        db_session.add(_make_user(tenant.id, "cajero", "cajero2@bodegapp.dev"))
        with pytest.raises(IntegrityError):
            await db_session.flush()

    async def test_same_username_allowed_across_tenants(self, db_session):
        tenant_a = Tenant(name="Bodega A", slug="bodega-a")
        tenant_b = Tenant(name="Bodega B", slug="bodega-b")
        db_session.add_all([tenant_a, tenant_b])
        await db_session.flush()

        db_session.add(_make_user(tenant_a.id, "cajero", "cajero.a@bodegapp.dev"))
        await db_session.flush()

        db_session.add(_make_user(tenant_b.id, "cajero", "cajero.b@bodegapp.dev"))
        await db_session.flush()  # must NOT raise

        result = await db_session.execute(select(User))
        assert len(result.scalars().all()) == 2

    async def test_user_requires_existing_tenant_fk(self, db_session):
        ghost_tenant_id = uuid.uuid4()
        db_session.add(_make_user(ghost_tenant_id, "huerfano", "huerfano@bodegapp.dev"))

        with pytest.raises(IntegrityError):
            await db_session.flush()
