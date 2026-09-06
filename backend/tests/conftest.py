"""Shared fixtures for the auth test suite.

Keys: a valid RSA pair + an ATTACKER pair (wrong key scenario, QA B2).
Keys are provisioned automatically by the session-scoped
`_provision_test_keys` fixture (QA-F04-01): existing keys at
BODEGAPP_TEST_KEYS_DIR are reused; a fresh set is generated otherwise,
so a clean clone or CI runner needs no manual setup.
All tests run against an isolated app instance whose DB dependency is
overridden with a fresh in-memory SQLite database.
"""

import os
import uuid
from pathlib import Path

import pytest
import pytest_asyncio
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app import models  # noqa: F401 — register models on Base.metadata
from app.core import security
from app.db.base import Base
from app.db.session import get_db_session
from app.main import create_app
from app.models import Tenant, User, UserRole

KEYS_DIR = Path(os.environ.get("BODEGAPP_TEST_KEYS_DIR", "/tmp/opencode/auth_keys"))
PRIVATE_KEY = KEYS_DIR / "test_private.pem"
PUBLIC_KEY = KEYS_DIR / "test_public.pem"
ATTACKER_PRIVATE_KEY = KEYS_DIR / "attacker_private.pem"

PASSWORD = "secreto-123"
OTHER_PASSWORD = "otro-secreto-456"


def _generate_rsa_keys(keys_dir: Path) -> None:
    """Write the test key set: test pair + attacker pair (PKCS#8/SPKI PEM)."""
    test_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    attacker_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    def _private_pem(key) -> bytes:
        return key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

    keys_dir.mkdir(parents=True, exist_ok=True)
    (keys_dir / "test_private.pem").write_bytes(_private_pem(test_key))
    (keys_dir / "test_public.pem").write_bytes(
        test_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )
    (keys_dir / "attacker_private.pem").write_bytes(_private_pem(attacker_key))


@pytest.fixture(scope="session", autouse=True)
def _provision_test_keys(tmp_path_factory):
    """QA-F04-01: make the suite independent of pre-provisioned RSA keys.

    If the three key files already exist at BODEGAPP_TEST_KEYS_DIR (or its
    default), they are reused as-is — no regeneration, stable local setup.
    Otherwise (clean clone / CI runner / partially provisioned dir) a fresh
    key set is generated with `cryptography` in a session temp dir and
    BODEGAPP_TEST_KEYS_DIR is pointed at it.

    Consumers (_use_test_keys, sign_with_attacker_key) resolve the
    module-level PRIVATE_KEY/PUBLIC_KEY/ATTACKER_PRIVATE_KEY globals at
    call time, so reassigning them here propagates everywhere.
    """
    global KEYS_DIR, PRIVATE_KEY, PUBLIC_KEY, ATTACKER_PRIVATE_KEY

    if all(path.is_file() for path in (PRIVATE_KEY, PUBLIC_KEY, ATTACKER_PRIVATE_KEY)):
        return

    keys_dir = tmp_path_factory.mktemp("bodegapp-test-keys")
    _generate_rsa_keys(keys_dir)
    os.environ["BODEGAPP_TEST_KEYS_DIR"] = str(keys_dir)
    KEYS_DIR = keys_dir
    PRIVATE_KEY = keys_dir / "test_private.pem"
    PUBLIC_KEY = keys_dir / "test_public.pem"
    ATTACKER_PRIVATE_KEY = keys_dir / "attacker_private.pem"


def _engine():
    return create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def _enable_fk(engine):
    @event.listens_for(engine.sync_engine, "connect")
    def _fk(dbapi_conn, _record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


async def _create_all(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(autouse=True)
def _use_test_keys(monkeypatch, tmp_path):
    """Point settings at the test key pair via env vars.

    get_settings is lru_cache'd, so the cache is cleared around each
    test — every consumer (security, auth_service, ...) re-resolves the
    Settings instance and sees the test configuration.
    """
    private = tmp_path / "jwt_private_key.pem"
    public = tmp_path / "jwt_public_key.pem"
    private.write_bytes(PRIVATE_KEY.read_bytes())
    public.write_bytes(PUBLIC_KEY.read_bytes())

    monkeypatch.setenv("BODEGAPP_JWT_PRIVATE_KEY_PATH", str(private))
    monkeypatch.setenv("BODEGAPP_JWT_PUBLIC_KEY_PATH", str(public))
    # Refresh rotation is intentionally NOT pinned here: tests exercise the
    # production default (enabled, QA-ST02-01). The kill-switch mode is
    # opted into explicitly by the tests that cover it.

    from app.core.config import get_settings

    get_settings.cache_clear()
    security.reset_jwt_keys()
    yield
    security.reset_jwt_keys()
    get_settings.cache_clear()


@pytest_asyncio.fixture
async def db_engine():
    engine = _engine()
    _enable_fk(engine)
    await _create_all(engine)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine):
    factory = async_sessionmaker(db_engine, expire_on_commit=False)
    async with factory() as session:
        yield session


def make_tenant(name: str = "Bodega Central", slug: str = "bodega-central") -> Tenant:
    return Tenant(name=name, slug=slug)


def make_user(tenant: Tenant, username: str = "admin", email: str | None = None,
              password: str = PASSWORD, role: UserRole = UserRole.owner) -> User:
    return User(
        tenant_id=tenant.id,
        username=username,
        email=email or f"{username}@bodegapp.dev",
        hashed_password=security.hash_password(password),
        full_name="Usuario de Prueba",
        role=role,
    )


async def seed_tenant_with_owner(db_session) -> tuple[Tenant, User]:
    tenant = make_tenant()
    db_session.add(tenant)
    await db_session.flush()  # tenant.id assigned by the default first
    owner = make_user(tenant, role=UserRole.owner)
    db_session.add(owner)
    await db_session.flush()
    return tenant, owner


@pytest_asyncio.fixture
async def app_client(db_engine):
    """HTTP client bound to a fresh app + overridden DB dependency.

    get_db_session commits on success; the override disables the commit
    (SQLite in-memory tests persist via the shared StaticPool session).
    """
    app = create_app()
    factory = async_sessionmaker(db_engine, expire_on_commit=False)

    async def _override():
        async with factory() as session:
            yield session
            await session.commit()

    app.dependency_overrides[get_db_session] = _override
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testapi") as client:
        yield client


@pytest_asyncio.fixture
async def seeded_client(app_client, db_session):
    """app_client with one tenant/owner seeded (username `admin`)."""
    await seed_tenant_with_owner(db_session)
    yield app_client


def login_payload(username: str = "admin", password: str = PASSWORD) -> dict:
    return {"username": username, "password": password}


async def do_login(client: AsyncClient) -> dict:
    response = await client.post("/api/v1/auth/login", json=login_payload())
    assert response.status_code == 200, response.text
    return response.json()


async def login_as(
    client: AsyncClient, username: str, password: str = PASSWORD
) -> dict:
    """Login as an arbitrary user and return the dual token pair."""
    response = await client.post(
        "/api/v1/auth/login", json={"username": username, "password": password}
    )
    assert response.status_code == 200, response.text
    return response.json()


def auth_headers(tokens: dict) -> dict:
    return {"Authorization": f"Bearer {tokens['access_token']}"}


def tienda_payload(**overrides) -> dict:
    """Default valid store-config request body for M-01 tests."""
    payload = {
        "nombre_comercial": "Bodega Central C.A.",
        "rif": "J-12345678-9",
        "razon_social": "Bodega Central Compañía Anónima",
        "direccion": "Av. Principal, Local 4, Caracas",
        "direccion_fiscal": "Av. Principal, Local 4, Caracas",
        "telefono": "0212-5551234",
        "moneda": "VES",
    }
    payload.update(overrides)
    return payload


def sign_with_attacker_key(payload: dict) -> str:
    """Sign a token with the attacker's private key (QA B2)."""
    import jwt

    return jwt.encode(
        payload, ATTACKER_PRIVATE_KEY.read_text(), algorithm="RS256"
    )
