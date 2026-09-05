# BodegApp Backend

FastAPI backend for BodegApp — multi-tenant inventory system for Venezuelan bodegas.
F0-03: application skeleton + multi-tenant schema · F0-04: JWT RS256 auth
with dual tokens (contratante/trabajo).

## Requirements

- Python 3.12 (pyenv: `pyenv local 3.12.0` or set a 3.12 interpreter)

## Setup

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Run

```bash
uvicorn app.main:app --reload
```

- API: http://localhost:8000/api/v1/health
- Docs (Swagger): http://localhost:8000/docs

## Tests

```bash
pytest
```

Tests use async in-memory SQLite (`sqlite+aiosqlite`) with FK enforcement enabled,
so no external database is needed for this suite. The RSA test keys (valid
pair + attacker pair) are provisioned automatically by a session-scoped
fixture: if `BODEGAPP_TEST_KEYS_DIR` already points to the three existing key
files they are reused, otherwise the suite generates a fresh key set with
`cryptography` in a temp directory — **no manual key provisioning is
required** in a clean clone or CI runner. The auth suite (42 tests)
covers the full login→refresh→logout lifecycle, expired tokens, wrong-key
signatures, alg=none/HS256 attacks, tenant isolation and rotation with
reuse detection. Coverage tip on Python 3.12.0: run
`COVERAGE_CORE=sysmon pytest --cov=app` (the default tracer misses lines
after `await` on 3.12.0; fixed upstream in 3.12.1+).

## Database migrations (Alembic)

The connection string comes from `BODEGAPP_DATABASE_URL` (env prefix `BODEGAPP_`).
Defaults to a local SQLite file for development; production uses PostgreSQL
(req 0-1, async driver `asyncpg`).

```bash
# Generate a new revision after changing models
alembic revision -m "describe change"

# Apply migrations
alembic upgrade head

# Rollback one revision
alembic downgrade -1
```

The initial revision `0001` creates `tenants`, `users`, and `store_configs` with:
- unique `tenants.slug`
- unique `(tenant_id, username)` per tenant — usernames are NOT globally unique
- one `store_configs` row per tenant (unique `tenant_id`)
- `ON DELETE CASCADE` from tenant to users/config

Revision `0002` adds `refresh_tokens` (hashed contractor tokens with
`revoked_at` and `rotated_to_id` for rotation/revocation, F0-04).

## Configuration

All settings come from environment variables with the `BODEGAPP_` prefix
(see `app/core/config.py`):

| Variable | Default | Description |
|----------|---------|-------------|
| `BODEGAPP_DATABASE_URL` | `sqlite+aiosqlite:///./bodegapp.db` | Async SQLAlchemy URL |
| `BODEGAPP_JWT_PRIVATE_KEY_PATH` | `secrets/jwt_private_key.pem` | RS256 private key (signing only) |
| `BODEGAPP_JWT_PUBLIC_KEY_PATH` | `secrets/jwt_public_key.pem` | RS256 public key (verification only) |
| `BODEGAPP_ACCESS_TOKEN_MINUTES` | `15` | Work token (access) lifetime |
| `BODEGAPP_REFRESH_TOKEN_DAYS` | `7` | Contractor token (refresh) lifetime |
| `BODEGAPP_JWT_CLOCK_LEEWAY_SECONDS` | `30` | Clock skew tolerance on verification |
| `BODEGAPP_REFRESH_ROTATION_ENABLED` | `false` | Rotate refresh on refresh; see note below |
| `BODEGAPP_CORS_ORIGINS` | `["http://localhost:5173"]` | Allowed origins (never `*`) |

## Authentication (F0-04) — JWT RS256, dual tokens

Architecture per `docs/INTEGRACION-BACKEND-FRONTEND.md` (contract §1-§2):

- **Token de trabajo** (access, `typ="access"`): 15 min, `Authorization: Bearer`.
- **Token contratante** (refresh, `typ="refresh"`): 7 days, only valid at
  `/auth/refresh` and `/auth/logout`. Persisted **hashed** (SHA-256 of the
  `jti`) in `refresh_tokens` — never plaintext. Logout revokes it; the
  residual access token dies by its own short life.
- Both tokens carry `tenant_id`; tenant context is derived from the JWT
  only (contract rule T5). `get_current_user` (app/api/deps.py) injects the
  authenticated identity for every protected endpoint.
- Algorithm pinned to RS256 on encode and decode: `alg=none` and HS256
  confusion attacks are rejected by construction.
- Password hashing: argon2 (passlib), bcrypt fallback for legacy hashes.

### Generating development keys

```bash
mkdir -p secrets
openssl genrsa -out secrets/jwt_private_key.pem 2048
openssl rsa -in secrets/jwt_private_key.pem -pubout -out secrets/jwt_public_key.pem
chmod 600 secrets/jwt_private_key.pem
```

`secrets/` is git-ignored; production keys are provisioned by infra
(Docker secrets / env-configured paths), never committed (QA B9).

### Rotation note (`BODEGAPP_REFRESH_ROTATION_ENABLED`)

Refresh rotation with theft detection is fully implemented: when enabled,
each refresh issues a new contractor token, revokes the old one and reuse
of a rotated token revokes the whole chain. It ships **disabled** because
the current frontend apiClient keeps the OLD refresh token after a
successful refresh (`frontend/src/lib/apiClient.ts` — it discards the
rotated one), so strict rotation would break active sessions at the
second refresh. Enable once the frontend persists the rotated token
atomically (contract rule T3).

### Auth endpoints

| Method | Path | Auth | Success | Main errors |
|--------|------|------|---------|-------------|
| POST | `/api/v1/auth/login` | — | `200` dual tokens | `401 CREDENCIALES_INVALIDAS` |
| POST | `/api/v1/auth/refresh` | refresh token | `200` new access (+ rotated refresh) | `401 REFRESH_INVALIDO` / `REFRESH_EXPIRADO` / `TOKEN_INVALIDO` |
| POST | `/api/v1/auth/logout` | refresh token in body | `200 {mensaje}` | idempotent — always 200 |
| GET | `/api/v1/auth/me` | access token | `200` identity + tenant_id | `401 TOKEN_AUSENTE` / `TOKEN_INVALIDO` / `TOKEN_EXPIRADO` |

Login accepts `username` OR `email` in the `username` field (the field
name matches the current frontend apiClient). All errors use the uniform
envelope: `{"error": {"codigo", "mensaje", "detalles?", "request_id?"}}`.

## Architecture

- `app/main.py` — FastAPI factory, CORS, routers, central error handlers
- `app/core/` — settings, `security.py` (RS256 JWT + argon2), `exceptions.py` (error catalog)
- `app/db/` — declarative `Base` + async engine/session
- `app/models/` — SQLAlchemy 2.0 ORM: `Tenant`, `User`, `StoreConfig`, `RefreshToken`
- `app/schemas/` — Pydantic v2 request/response schemas (`auth.py` for F0-04)
- `app/services/` — business logic (`auth_service.py`: login/refresh/logout/rotation)
- `app/api/deps.py` — `get_current_user` dependency (tenant from JWT, rule T5)
- `migrations/` — Alembic async env
- `docs/ADR-001-multi-tenant.md` — isolation strategy decision (shared schema + RLS)

## Multi-tenancy (summary)

Shared schema with `tenant_id` on every business table + PostgreSQL Row Level
Security (decision detail in `docs/ADR-001-multi-tenant.md`). RLS policies are
enabled in a follow-up revision together with the first Phase 1 business
endpoints; the auth layer already carries `tenant_id` inside both tokens and
`get_current_user` exposes it to downstream handlers (contract rule T5).

Error responses follow `docs/INTEGRACION-BACKEND-FRONTEND.md` §3.2 (Spanish
messages, uniform JSON envelope with `codigo`/`mensaje`/`detalles`/
`request_id`) — implemented as central exception handlers in `app/main.py`.
