# ADR-001 — Estrategia de aislamiento multi-tenant

- **Estado**: Aceptado
- **Fecha**: 2026-09-03
- **Ref MAT**: F0-03
- **Decididores**: Nelson (Backend), con dirección del Director de Tecnología
- **Trazabilidad**: REQUERIMIENTOS.md 0-5 (Aplicación Multi-Tenant), INTEGRACION-BACKEND-FRONTEND.md regla T5

## Contexto

BodegApp es un sistema de inventario multi-tenant para bodegas del mercado venezolano. Cada tenant (bodega) tiene sus propios productos, fiados, proveedores, usuarios y configuración de tienda. Requisitos que condicionan la decisión:

1. **Regla T5** (contrato de integración): el aislamiento se deriva **del token**, jamás de parámetros de request.
2. Stack mandatario: PostgreSQL + SQLAlchemy 2.0 async + FastAPI (req 0-1).
3. Equipo pequeño, ops mínimas: no hay equipo de DBA dedicado.
4. Volumen esperado: muchos tenants pequeños (bodegas de barrio), no pocos tenants enormes.
5. Tests de integración con DB real vía testcontainers (ESTANDARES-CODIGO.md §1).

## Opciones consideradas

### Opción A — Schema por tenant (database-per-tenant ligero)

Cada tenant vive en su propio schema PostgreSQL (`tenant_bodega01`, `tenant_bodega02`...), sin columna `tenant_id`.

- **Pros**: aislamiento físico fuerte; backup/restore por tenant; un tenant no puede ver datos de otro por construcción (no por política).
- **Contras**:
  - Migraciones multiplicadas: una cadena Alembic por schema (cientos de tenants = cientos de ejecuciones por deploy). Alembic no gestiona multi-schema nativamente.
  - Provisionamiento de tenant = crear schema + correr migraciones: lento, propenso a drift entre schemas.
  - Pool de conexiones fragmentado o cambio de schema por transacción (`SET search_path`): complejidad real con SQLAlchemy async.
  - Consultas cross-tenant (reportes, soporte, facturación del SaaS) requieren UNION dinámico sobre schemas.
  - RLS de PostgreSQL no aplica por schema de forma útil; la seguridad queda solo en la app.

### Opción B — Schema compartido + columna `tenant_id` + **RLS** (elegida)

Una base, un schema, todas las tablas llevan `tenant_id`, y PostgreSQL aplica **Row Level Security**: cada política filtra filas por `app.current_tenant`, variable de sesión seteada por transacción desde el token (regla T5).

- **Pros**:
  - **Una sola cadena de migraciones** Alembic — ops simples, drift imposible.
  - Aislamiento **en la base de datos**, no solo en la app: aunque un desarrollador olvide un `WHERE tenant_id = ...`, la política RLS bloquea la fuga. Defensa en profundidad.
  - Funciona naturalmente con SQLAlchemy async: un pool, un `SET LOCAL app.current_tenant` al inicio de cada transacción.
  - Provisionar tenant = un INSERT en `tenants`: instantáneo.
  - Consultas cross-tenant triviales para admin/soporte del SaaS.
- **Contras**:
  - RLS es específico de PostgreSQL (aceptable: es el motor mandatario, req 0-1).
  - Overhead por fila en cada query (mitigado con índices que incluyan `tenant_id`).
  - SQLite (tests locales rápidos) no tiene RLS: los tests de unidad/modelo validan la restricción compuesta `(tenant_id, username)`; el aislamiento RLS real se prueba con testcontainers PostgreSQL (exigido por estándar).
  - Riesgo de sesión con tenant mal seteado: mitigado con `SET LOCAL` (scope transacción, no sesión) y forzando el set en la dependencia de sesión.

### Opción C — Base de datos por tenant

Descartada sin evaluación profunda: same perfil que A con aún más overhead (conexiones, monitoring, backups) sin beneficio adicional para tenants pequeños.

## Decisión

**Opción B**: schema compartido con `tenant_id` en toda tabla de negocio + **políticas RLS de PostgreSQL**, aplicadas a partir de F0-04/F1 con el tenant derivado del token (regla T5), vía `SET LOCAL app.current_tenant` por transacción.

Coincide con la recomendación del Director (RLS por simplicidad operativa) y la refuerzo por un motivo técnico: con SQLAlchemy async y un solo pool, RLS + `SET LOCAL` es el único modelo donde el aislamiento **no depende de la disciplina del código de cada endpoint**. En schema-por-tenant, el equivalente (`search_path`) es global de sesión: una fuga de estado entre requests en un pool compartido es el bug más caro que este sistema puede tener.

## Consecuencias

1. Toda tabla de negocio futura (productos, fiados, proveedores...) DEBE llevar `tenant_id` NOT NULL con FK a `tenants.id` e índice compuesto que lidere las queries por tenant.
2. La revisión inicial de Alembic (este cambio) crea las 3 tablas base sin políticas; las políticas RLS se agregan en la revisión de F0-04 (auth), cuando exista el flujo que setea `app.current_tenant`.
3. Tests de aislamiento RLS viven como integración con testcontainers PostgreSQL (estándar §1); los tests SQLite de esta entrega validan unicidad compuesta y FK.
4. Índices: priorizar índices que empiecen por `tenant_id` (ej: `uq_user_tenant_username`) para que RLS + queries no degraden.
5. Reversión: si un tenant exige aislamiento físico contractual, migrar ese tenant a base dedicada es un proyecto puntual, no un rediseño del modelo.
