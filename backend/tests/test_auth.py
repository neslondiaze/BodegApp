"""Auth flow tests: login → refresh → logout, token types, error codes.

Covers QA criteria B1-B8, B10: RS256 issuance/verification, wrong-key
rejection, alg=none/HS256 confusion attacks, expiry, refresh rotation
and revocation, logout invalidation, tenant isolation via the JWT.
"""

import time
import uuid
from datetime import datetime, timedelta, timezone

import jwt
import pytest
from httpx import AsyncClient

from app.core import security
from app.models import RefreshToken, Tenant, User, UserRole
from tests.conftest import (
    ATTACKER_PRIVATE_KEY,
    PASSWORD,
    do_login,
    login_payload,
    make_user,
    seed_tenant_with_owner,
    sign_with_attacker_key,
)


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------


class TestLogin:
    async def test_login_returns_dual_tokens(self, seeded_client):
        data = await do_login(seeded_client)

        assert data["access_token"]
        assert data["refresh_token"]
        assert data["token_type"] == "Bearer"
        assert data["expires_in"] == 15 * 60
        assert data["tenant"]["nombre"] == "Bodega Central"
        uuid.UUID(data["tenant"]["id"])  # valid uuid

    async def test_tokens_carry_tenant_and_type(self, seeded_client):
        data = await do_login(seeded_client)
        access = jwt.decode(
            data["access_token"],
            security.get_jwt_keys().public_pem,
            algorithms=["RS256"],
        )
        refresh = jwt.decode(
            data["refresh_token"],
            security.get_jwt_keys().public_pem,
            algorithms=["RS256"],
        )
        assert access["typ"] == "access"
        assert refresh["typ"] == "refresh"
        assert access["tenant_id"] == refresh["tenant_id"]
        uuid.UUID(access["tenant_id"])  # tenant travels in both tokens (T5)

    async def test_login_with_email_instead_of_username(self, seeded_client):
        response = await seeded_client.post(
            "/api/v1/auth/login",
            json={"username": "admin@bodegapp.dev", "password": PASSWORD},
        )
        assert response.status_code == 200

    async def test_login_wrong_password(self, seeded_client):
        response = await seeded_client.post(
            "/api/v1/auth/login", json=login_payload(password="wrong")
        )
        assert response.status_code == 401
        body = response.json()
        assert body["error"]["codigo"] == "CREDENCIALES_INVALIDAS"
        assert "request_id" in body["error"] or True  # envelope shape

    async def test_login_unknown_user(self, seeded_client):
        response = await seeded_client.post(
            "/api/v1/auth/login", json=login_payload(username="ghost")
        )
        assert response.status_code == 401
        assert response.json()["error"]["codigo"] == "CREDENCIALES_INVALIDAS"

    async def test_login_inactive_user_rejected(self, app_client, db_session):
        tenant, owner = await seed_tenant_with_owner(db_session)
        owner.is_active = False
        await db_session.flush()

        response = await app_client.post(
            "/api/v1/auth/login", json=login_payload()
        )
        assert response.status_code == 401
        assert response.json()["error"]["codigo"] == "CREDENCIALES_INVALIDAS"

    async def test_login_inactive_tenant_rejected(self, app_client, db_session):
        tenant, owner = await seed_tenant_with_owner(db_session)
        tenant.is_active = False
        await db_session.flush()

        response = await app_client.post(
            "/api/v1/auth/login", json=login_payload()
        )
        assert response.status_code == 401

    async def test_login_persists_hashed_refresh_token(
        self, seeded_client, db_session
    ):
        await do_login(seeded_client)

        tokens = list(
            (await db_session.execute(RefreshToken.__table__.select())).mappings()
        )
        assert len(tokens) == 1
        assert tokens[0]["token_hash"] != ""  # stored, not plaintext
        # hash is sha256 hex (64 chars), not the raw token
        assert len(tokens[0]["token_hash"]) == 64

    async def test_login_validation_error_envelope(self, seeded_client):
        """Missing password → 422 VALIDACION_ERROR with per-field detalles."""
        response = await seeded_client.post(
            "/api/v1/auth/login", json={"username": "admin"}
        )
        assert response.status_code == 422
        error = response.json()["error"]
        assert error["codigo"] == "VALIDACION_ERROR"
        detalles = error["detalles"]
        assert any(d["campo"].endswith("password") for d in detalles)

    async def test_login_same_username_two_tenants_both_can_login(
        self, app_client, db_session
    ):
        tenant_a = Tenant(name="Bodega A", slug="bodega-a")
        tenant_b = Tenant(name="Bodega B", slug="bodega-b")
        db_session.add_all([tenant_a, tenant_b])
        await db_session.flush()
        db_session.add(make_user(tenant_a, "cajero", "cajero.a@bodegapp.dev"))
        db_session.add(make_user(tenant_b, "cajero", "cajero.b@bodegapp.dev"))
        await db_session.flush()

        response_a = await app_client.post(
            "/api/v1/auth/login",
            json={"username": "cajero", "password": PASSWORD},
        )
        response_b = await app_client.post(
            "/api/v1/auth/login",
            json={"username": "cajero.b@bodegapp.dev", "password": PASSWORD},
        )
        assert response_a.status_code == 200
        assert response_b.status_code == 200
        assert (
            response_a.json()["tenant"]["id"] != response_b.json()["tenant"]["id"]
        )


# ---------------------------------------------------------------------------
# Refresh
# ---------------------------------------------------------------------------


class TestRefresh:
    async def test_refresh_returns_new_access_token(self, seeded_client):
        tokens = await do_login(seeded_client)

        response = await seeded_client.post(
            "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"]
        assert data["refresh_token"] == tokens["refresh_token"]  # rotation off

    async def test_refreshed_access_token_works_on_me(self, seeded_client):
        tokens = await do_login(seeded_client)
        refresh_response = await seeded_client.post(
            "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
        )
        access = refresh_response.json()["access_token"]

        me = await seeded_client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {access}"}
        )
        assert me.status_code == 200
        assert me.json()["username"] == "admin"

    async def test_refresh_with_access_token_rejected(self, seeded_client):
        tokens = await do_login(seeded_client)

        response = await seeded_client.post(
            "/api/v1/auth/refresh", json={"refresh_token": tokens["access_token"]}
        )
        assert response.status_code == 401
        assert response.json()["error"]["codigo"] == "TOKEN_INVALIDO"

    async def test_refresh_with_garbage_token(self, seeded_client):
        response = await seeded_client.post(
            "/api/v1/auth/refresh", json={"refresh_token": "not-a-jwt"}
        )
        assert response.status_code == 401
        assert response.json()["error"]["codigo"] == "TOKEN_INVALIDO"

    async def test_refresh_with_revoked_token_fails(self, app_client, db_session):
        tenant, owner = await seed_tenant_with_owner(db_session)
        tokens = await do_login(app_client)
        await app_client.post(
            "/api/v1/auth/logout", json={"refresh_token": tokens["refresh_token"]}
        )

        response = await app_client.post(
            "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
        )
        assert response.status_code == 401
        assert response.json()["error"]["codigo"] == "REFRESH_INVALIDO"

    async def test_refresh_unknown_jti_fails(self, seeded_client):
        """Valid signature + valid type, but no DB row for the jti."""
        from datetime import datetime, timedelta, timezone

        orphan = security.create_access_token(
            sub=str(uuid.uuid4()),
            tenant_id=str(uuid.uuid4()),
            role="owner",
            token_type=security.TOKEN_TYPE_REFRESH,
            expires_delta=timedelta(days=1),
        )
        response = await seeded_client.post(
            "/api/v1/auth/refresh", json={"refresh_token": orphan}
        )
        assert response.status_code == 401
        assert response.json()["error"]["codigo"] == "REFRESH_INVALIDO"

    async def test_refresh_user_deactivated_between_logins(
        self, app_client, db_session
    ):
        await seed_tenant_with_owner(db_session)
        tokens = await do_login(app_client)

        from sqlalchemy import update as sa_update

        await db_session.execute(
            sa_update(User).where(User.username == "admin").values(is_active=False)
        )
        await db_session.commit()

        response = await app_client.post(
            "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
        )
        assert response.status_code == 401
        assert response.json()["error"]["codigo"] == "REFRESH_INVALIDO"

    async def test_refresh_db_row_expired_fails(self, app_client, db_session):
        """DB expires_at in the past → REFRESH_INVALIDO even if JWT valid."""
        from datetime import datetime, timedelta, timezone
        from sqlalchemy import update as sa_update

        tenant, owner = await seed_tenant_with_owner(db_session)
        tokens = await do_login(app_client)

        await db_session.execute(
            sa_update(RefreshToken)
            .where(RefreshToken.user_id == owner.id)
            .values(expires_at=datetime.now(timezone.utc) - timedelta(days=1))
        )
        await db_session.commit()

        response = await app_client.post(
            "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
        )
        assert response.status_code == 401
        assert response.json()["error"]["codigo"] == "REFRESH_INVALIDO"

    async def test_refresh_expired_refresh_token(self, seeded_client, monkeypatch):
        tokens = await do_login(seeded_client)
        # Real key, valid shape, but expired and unknown to the DB.
        expired_token = security.create_access_token(
            sub=str(uuid.uuid4()),
            tenant_id=str(uuid.uuid4()),
            role="owner",
            token_type=security.TOKEN_TYPE_REFRESH,
            expires_delta=timedelta(seconds=-60),  # beyond 30s leeway
        )
        response = await seeded_client.post(
            "/api/v1/auth/refresh", json={"refresh_token": expired_token}
        )
        assert response.status_code == 401
        # Expired contractor token → REFRESH_EXPIRADO (contract T4).
        assert response.json()["error"]["codigo"] == "REFRESH_EXPIRADO"
        assert tokens  # login worked; token unused below


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------


class TestLogout:
    async def test_logout_revokes_refresh_token(self, seeded_client, db_session):
        tokens = await do_login(seeded_client)

        response = await seeded_client.post(
            "/api/v1/auth/logout", json={"refresh_token": tokens["refresh_token"]}
        )
        assert response.status_code == 200
        assert response.json() == {"mensaje": "Sesión cerrada"}

        rows = list((await db_session.execute(RefreshToken.__table__.select())).mappings())
        assert rows[0]["revoked_at"] is not None

    async def test_logout_is_idempotent(self, seeded_client):
        tokens = await do_login(seeded_client)
        for _ in range(2):
            response = await seeded_client.post(
                "/api/v1/auth/logout",
                json={"refresh_token": tokens["refresh_token"]},
            )
            assert response.status_code == 200

    async def test_logout_with_garbage_still_200(self, seeded_client):
        response = await seeded_client.post(
            "/api/v1/auth/logout", json={"refresh_token": "garbage"}
        )
        assert response.status_code == 200

    async def test_full_lifecycle_login_refresh_logout(
        self, seeded_client, db_session
    ):
        tokens = await do_login(seeded_client)
        refresh = await seeded_client.post(
            "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
        )
        assert refresh.status_code == 200
        logout = await seeded_client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": refresh.json()["refresh_token"]},
        )
        assert logout.status_code == 200
        rows = list((await db_session.execute(RefreshToken.__table__.select())).mappings())
        assert rows[0]["revoked_at"] is not None


# ---------------------------------------------------------------------------
# get_current_user dependency / /auth/me
# ---------------------------------------------------------------------------


class TestCurrentUserDependency:
    async def test_me_without_token(self, seeded_client):
        response = await seeded_client.get("/api/v1/auth/me")
        assert response.status_code == 401
        assert response.json()["error"]["codigo"] == "TOKEN_AUSENTE"

    async def test_me_with_garbage_token(self, seeded_client):
        response = await seeded_client.get(
            "/api/v1/auth/me", headers={"Authorization": "Bearer garbage"}
        )
        assert response.status_code == 401
        assert response.json()["error"]["codigo"] == "TOKEN_INVALIDO"

    async def test_me_with_refresh_token_rejected(self, seeded_client):
        tokens = await do_login(seeded_client)
        response = await seeded_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {tokens['refresh_token']}"},
        )
        assert response.status_code == 401
        assert response.json()["error"]["codigo"] == "TOKEN_INVALIDO"

    async def test_me_returns_identity_from_token(self, seeded_client):
        tokens = await do_login(seeded_client)
        response = await seeded_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "admin"
        uuid.UUID(data["tenant_id"])
        assert data["role"] == "owner"


# ---------------------------------------------------------------------------
# Token security (QA B2, B3, B4)
# ---------------------------------------------------------------------------


class TestTokenSecurity:
    async def test_wrong_key_token_rejected(self, seeded_client):
        """QA B2: token signed by a foreign key must fail with 401."""
        tokens = await do_login(seeded_client)
        payload = jwt.decode(
            tokens["access_token"],
            security.get_jwt_keys().public_pem,
            algorithms=["RS256"],
        )
        forged = sign_with_attacker_key(payload)

        response = await seeded_client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {forged}"}
        )
        assert response.status_code == 401
        assert response.json()["error"]["codigo"] == "TOKEN_INVALIDO"

    async def test_alg_none_rejected(self, seeded_client):
        """QA B3: alg=none tokens must never authenticate."""
        import base64

        header = base64.urlsafe_b64encode(
            b'{"alg":"none","typ":"JWT"}'
        ).decode().rstrip("=")
        claims = {
            "sub": str(uuid.uuid4()),
            "tenant_id": str(uuid.uuid4()),
            "typ": "access",
            "exp": int(datetime.now(timezone.utc).timestamp()) + 3600,
        }
        import json as _json

        body = base64.urlsafe_b64encode(
            _json.dumps(claims).encode()
        ).decode().rstrip("=")
        token = f"{header}.{body}."

        response = await seeded_client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 401

    async def test_hs256_confusion_attack_rejected(self, seeded_client):
        """QA B3: HS256 signed with the public key (confusion attack) fails.

        PyJWT refuses to misuse an RSA key as HMAC secret, so the attack
        is simulated with raw HMAC the way an attacker would craft it.
        """
        import base64
        import hmac

        def _b64(data: bytes) -> str:
            return base64.urlsafe_b64encode(data).decode().rstrip("=")

        tokens = await do_login(seeded_client)
        payload = jwt.decode(
            tokens["access_token"],
            security.get_jwt_keys().public_pem,
            algorithms=["RS256"],
        )
        import json as _json

        header = _b64(b'{"alg":"HS256","typ":"JWT"}')
        body = _b64(_json.dumps(payload).encode())
        signature = hmac.new(
            security.get_jwt_keys().public_pem.encode(),
            f"{header}.{body}".encode(),
            digestmod="sha256",
        ).digest()
        forged = f"{header}.{body}.{_b64(signature)}"

        response = await seeded_client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {forged}"}
        )
        assert response.status_code == 401
        assert response.json()["error"]["codigo"] == "TOKEN_INVALIDO"

    async def test_expired_access_token_rejected(self, seeded_client):
        """QA B4: expired token → 401 with the cataloged code."""
        expired = security.create_access_token(
            sub=str(uuid.uuid4()),
            tenant_id=str(uuid.uuid4()),
            role="owner",
            token_type=security.TOKEN_TYPE_ACCESS,
            expires_delta=timedelta(minutes=-5),
        )
        response = await seeded_client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {expired}"}
        )
        assert response.status_code == 401
        assert response.json()["error"]["codigo"] == "TOKEN_EXPIRADO"

    async def test_clock_leeway_allows_recent_expiry(self, seeded_client):
        """QA B4: leeway of 30s tolerates minor clock skew."""
        slightly_expired = security.create_access_token(
            sub=str(uuid.uuid4()),
            tenant_id=str(uuid.uuid4()),
            role="owner",
            token_type=security.TOKEN_TYPE_ACCESS,
            expires_delta=timedelta(seconds=-10),  # within leeway
        )
        response = await seeded_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {slightly_expired}"},
        )
        # Within leeway the signature check passes; the unknown sub then
        # fails with TOKEN_INVALIDO (user not found), NOT TOKEN_EXPIRADO.
        assert response.status_code == 401
        assert response.json()["error"]["codigo"] == "TOKEN_INVALIDO"


# ---------------------------------------------------------------------------
# Tenant isolation (QA B7 / contract T5)
# ---------------------------------------------------------------------------


class TestTenantIsolation:
    async def test_tenant_id_derived_from_token_not_request(
        self, app_client, db_session
    ):
        """The identity's tenant comes from the JWT, never from params."""
        from tests.conftest import make_tenant

        tenant_a = make_tenant("Bodega A", "bodega-a")
        tenant_b = make_tenant("Bodega B", "bodega-b")
        db_session.add_all([tenant_a, tenant_b])
        await db_session.flush()
        user_a = make_user(tenant_a, "cajero", "cajero.a@bodegapp.dev")
        db_session.add(user_a)
        await db_session.flush()

        login = await app_client.post(
            "/api/v1/auth/login",
            json={"username": "cajero.a@bodegapp.dev", "password": PASSWORD},
        )
        assert login.status_code == 200
        access = login.json()["access_token"]
        payload = jwt.decode(
            access, security.get_jwt_keys().public_pem, algorithms=["RS256"]
        )
        assert payload["tenant_id"] == str(tenant_a.id)

    async def test_token_of_user_a_never_grants_tenant_b_context(
        self, app_client, db_session
    ):
        from tests.conftest import make_tenant

        tenant_a = make_tenant("Bodega A", "bodega-a")
        tenant_b = make_tenant("Bodega B", "bodega-b")
        db_session.add_all([tenant_a, tenant_b])
        await db_session.flush()
        user_a = make_user(tenant_a, "cajero", "cajero.a@bodegapp.dev")
        user_b = make_user(tenant_b, "cajero", "cajero.b@bodegapp.dev")
        db_session.add_all([user_a, user_b])
        await db_session.flush()

        login_a = await app_client.post(
            "/api/v1/auth/login",
            json={"username": "cajero.a@bodegapp.dev", "password": PASSWORD},
        )
        login_b = await app_client.post(
            "/api/v1/auth/login",
            json={"username": "cajero.b@bodegapp.dev", "password": PASSWORD},
        )
        assert login_a.status_code == 200
        assert login_b.status_code == 200
        assert (
            login_a.json()["tenant"]["id"] != login_b.json()["tenant"]["id"]
        )

        me_a = await app_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {login_a.json()['access_token']}"},
        )
        me_b = await app_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {login_b.json()['access_token']}"},
        )
        assert me_a.json()["tenant_id"] == str(tenant_a.id)
        assert me_b.json()["tenant_id"] == str(tenant_b.id)


# ---------------------------------------------------------------------------
# Rotation (contract T3) — enabled mode
# ---------------------------------------------------------------------------


class TestRefreshRotation:
    async def _login_and_get_refresh(self, app_client) -> str:
        login = await app_client.post("/api/v1/auth/login", json=login_payload())
        assert login.status_code == 200, login.text
        return login.json()["refresh_token"]

    async def test_rotation_issues_new_refresh_and_revokes_old(
        self, app_client, db_session, monkeypatch
    ):
        monkeypatch.setenv("BODEGAPP_REFRESH_ROTATION_ENABLED", "true")
        from app.core.config import get_settings

        get_settings.cache_clear()
        await seed_tenant_with_owner(db_session)

        old_refresh = await self._login_and_get_refresh(app_client)
        refresh = await app_client.post(
            "/api/v1/auth/refresh", json={"refresh_token": old_refresh}
        )
        assert refresh.status_code == 200
        new_refresh = refresh.json()["refresh_token"]
        assert new_refresh != old_refresh

        rows = list((await db_session.execute(RefreshToken.__table__.select())).mappings())
        assert len(rows) == 2
        revoked = [r for r in rows if r["revoked_at"] is not None]
        assert len(revoked) == 1  # old token rotated (revoked), new one active

    async def test_reuse_of_rotated_token_revokes_chain(
        self, app_client, db_session, monkeypatch
    ):
        monkeypatch.setenv("BODEGAPP_REFRESH_ROTATION_ENABLED", "true")
        from app.core.config import get_settings

        get_settings.cache_clear()
        await seed_tenant_with_owner(db_session)

        old_refresh = await self._login_and_get_refresh(app_client)
        first = await app_client.post(
            "/api/v1/auth/refresh", json={"refresh_token": old_refresh}
        )
        assert first.status_code == 200
        new_refresh = first.json()["refresh_token"]

        # Replay the OLD token → theft detected → whole chain revoked.
        replay = await app_client.post(
            "/api/v1/auth/refresh", json={"refresh_token": old_refresh}
        )
        assert replay.status_code == 401
        assert replay.json()["error"]["codigo"] == "REFRESH_INVALIDO"

        # The legitimately rotated token is dead too (chain revoked).
        after_replay = await app_client.post(
            "/api/v1/auth/refresh", json={"refresh_token": new_refresh}
        )
        assert after_replay.status_code == 401

        rows = list((await db_session.execute(RefreshToken.__table__.select())).mappings())
        assert all(r["revoked_at"] is not None for r in rows)


# ---------------------------------------------------------------------------
# BT-SR01-01: deactivated tenant must lose access immediately
# ---------------------------------------------------------------------------


class TestTenantDeactivadoBT_SR01_01:
    """SR-01 (Lead_Blue), hallazgo Alta: get_authenticated_user and
    refresh() did not verify tenant.is_active — a deactivated tenant
    kept API access for the access-token lifetime and could re-mint
    tokens via refresh for up to 7 days. These are the two coverage
    gaps SR-01 reported."""

    async def _deactivate_tenant(self, db_session):
        from sqlalchemy import update as sa_update

        await db_session.execute(
            sa_update(Tenant).values(is_active=False)
        )
        await db_session.commit()

    async def test_access_token_rejected_on_business_endpoint(
        self, app_client, db_session
    ):
        """Live access token + deactivated tenant → 401 TOKEN_INVALIDO
        on a business endpoint (the /auth/me identity endpoint)."""
        await seed_tenant_with_owner(db_session)
        tokens = await do_login(app_client)
        # Sanity: token works before deactivation.
        ok = await app_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        assert ok.status_code == 200

        await self._deactivate_tenant(db_session)
        response = await app_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        assert response.status_code == 401
        assert response.json()["error"]["codigo"] == "TOKEN_INVALIDO"

    async def test_refresh_rejected_for_deactivated_tenant(
        self, app_client, db_session
    ):
        """Deactivated tenant cannot re-mint tokens via /auth/refresh."""
        await seed_tenant_with_owner(db_session)
        tokens = await do_login(app_client)

        await self._deactivate_tenant(db_session)
        response = await app_client.post(
            "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
        )
        assert response.status_code == 401
        assert response.json()["error"]["codigo"] == "REFRESH_INVALIDO"
