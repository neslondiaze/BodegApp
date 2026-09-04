# BodegApp Backend

FastAPI backend for BodegApp — multi-tenant inventory system for Venezuelan bodegas.
This is **Part 1 (F0-03)**: application skeleton + multi-tenant schema (tenants, users, store_configs).

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
so no external database is needed for this suite.

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

## Configuration

All settings come from environment variables with the `BODEGAPP_` prefix
(see `app/core/config.py`):

| Variable | Default | Description |
|----------|---------|-------------|
| `BODEGAPP_DATABASE_URL` | `sqlite+aiosqlite:///./bodegapp.db` | Async SQLAlchemy URL |
| `BODEGAPP_JWT_PRIVATE_KEY_PATH` | `secrets/jwt_private_key.pem` | RS256 private key (used from F0-04) |
| `BODEGAPP_JWT_PUBLIC_KEY_PATH` | `secrets/jwt_public_key.pem` | RS256 public key (used from F0-04) |
| `BODEGAPP_ACCESS_TOKEN_MINUTES` | `15` | Access token lifetime |
| `BODEGAPP_REFRESH_TOKEN_DAYS` | `7` | Refresh token lifetime |
| `BODEGAPP_CORS_ORIGINS` | `["http://localhost:5173"]` | Allowed origins (never `*`) |

## Architecture

- `app/main.py` — FastAPI factory, CORS, health router at `/api/v1/health`
- `app/core/` — settings (pydantic-settings)
- `app/db/` — declarative `Base` + async engine/session
- `app/models/` — SQLAlchemy 2.0 ORM: `Tenant`, `User`, `StoreConfig`
- `app/schemas/` — Pydantic v2 request/response schemas
- `migrations/` — Alembic async env
- `docs/ADR-001-multi-tenant.md` — isolation strategy decision (shared schema + RLS)

## Multi-tenancy (summary)

Shared schema with `tenant_id` on every business table + PostgreSQL Row Level
Security (decision detail in `docs/ADR-001-multi-tenant.md`). RLS policies are
enabled in a follow-up revision together with auth (F0-04), since tenant context
is derived from the JWT (contract rule T5).

Error responses follow `docs/INTEGRACION-BACKEND-FRONTEND.md` (Spanish messages,
uniform JSON envelope). This skeleton ships the health endpoint only; the error
envelope handler lands with the first business endpoints.
