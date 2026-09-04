# BodegApp — Contrato de Integración Backend ↔ Frontend

> Documento vinculante entre Nelson (Backend, `backend/`) y Noris (Frontend, `frontend/`). Todo endpoint, formato de error y flujo de autenticación se rige por este contrato. Cambios solo por acuerdo bilateral documentado (plantilla: `docs/plantillas/PLANTILLA-INTEGRACION.md`) y en el mismo PR que el código.

## Ruta rápida

1. Login → backend emite **token contratante** (refresh, larga duración) + **token de trabajo** (access, corta duración).
2. Frontend usa el token de trabajo en cada request (`Authorization: Bearer <access>`).
3. Al recibir 401, el frontend ejecuta refresh con el token contratante y reintenta una sola vez.
4. Logout (o refresh fallido) → token contratante revocado → redirigir a login.

---

## 1. Arquitectura de tokens dual

BodegApp usa dos tokens JWT firmados con **RS256** (requerimiento 0-1/0-2):

| Token | Uso | Duración | Almacenamiento en frontend |
|-------|-----|----------|----------------------------|
| **Contratante** (refresh) | Renovar el token de trabajo. Único canal para obtener nuevos access tokens. | Larga (sesión de negocio; valor exacto define Nelson en F0-04 y se documenta aquí) | Seguro: `httpOnly` cookie o memoria — nunca `localStorage` |
| **Trabajo** (access) | Autenticar cada llamada a la API. | Corta (15 minutos por defecto; ajustable en F0-04) | Memoria (estado de app) |

### Reglas del modelo

| # | Regla |
|---|-------|
| T1 | El token de trabajo **nunca** se persiste en `localStorage` ni `sessionStorage` (XSS). |
| T2 | El token contratante solo sale del frontend hacia el endpoint de refresh. Jamás hacia otros endpoints. |
| T3 | El refresh es **una sola ventana activa por sesión**: un refresh exitoso puede rotar el token contratante (detección de robo); el frontend debe reemplazarlo atómicamente. |
| T4 | Un access token vencido produce `401` con código `TOKEN_EXPIRADO`; un refresh fallido produce `401` con `REFRESH_INVALIDO` → logout inmediato. |
| T5 | Los tokens llevan el identificador de tenant; el backend deriva el aislamiento de datos del token, jamás de un parámetro de request. |
| T6 | Revocación: logout revoca el token contratante en backend (denylist/base de datos); el access residual expira por su corta vida. |

---

## 2. Flujo login → refresh → logout

### 2.1 Login

```
POST /api/v1/auth/login
{ "usuario": "...", "password": "..." }
```

Éxito (`200`):

```json
{
  "access_token": "<JWT trabajo, ~15 min>",
  "refresh_token": "<JWT contratante, larga duración>",
  "token_type": "Bearer",
  "expires_in": 900,
  "tenant": { "id": "uuid", "nombre": "Bodega Central" }
}
```

Errores: `401 CREDENCIALES_INVALIDAS`.

### 2.2 Uso del token de trabajo

```
Authorization: Bearer <access_token>
```

Todo endpoint funcional (excepto `/auth/login` y `/auth/refresh`) rechaza sin este header con `401 TOKEN_AUSENTE`.

### 2.3 Refresh (rotación del token de trabajo)

```
POST /api/v1/auth/refresh
{ "refresh_token": "<JWT contratante>" }
```

Éxito (`200`): misma forma que la respuesta de login (puede incluir nuevo `refresh_token` si hay rotación — regla T3).

Errores: `401 REFRESH_INVALIDO` / `401 REFRESH_EXPIRADO` → el frontend **debe** ejecutar logout local y redirigir a login.

### 2.4 Diagrama del ciclo

```
┌──────────┐  login (credenciales)   ┌──────────┐
│ Frontend │ ──────────────────────▶ │ Backend  │
│          │ ◀── access + refresh ── │ FastAPI  │
│          │                         └──────────┘
│          │  Bearer access (requests funcionales)
│          │ ──────────────────────▶ ┌──────────┐
│          │ ◀─────── 200 ────────── │ FastAPI  │
│          │                         └──────────┘
│          │  401 TOKEN_EXPIRADO (reintento único)
│          │  POST /auth/refresh ──▶ ┌──────────┐
│          │ ◀── nuevo access ───── │ FastAPI  │
│          │                         └──────────┘
│          │  401 REFRESH_INVALIDO
│          │  POST /auth/logout ──▶  ┌──────────┐
│          │  (revoca contratante)   │ FastAPI  │
└──────────┘                         └──────────┘
```

### 2.5 Logout

```
POST /api/v1/auth/logout
Authorization: Bearer <access>
{ "refresh_token": "<JWT contratante>" }
```

Éxito (`200`): `{ "mensaje": "Sesión cerrada" }`. El backend revoca el token contratante; el frontend limpia tokens en memoria y redirige a login.

### 2.6 Reglas del frontend (obligatorias para Noris)

| # | Regla |
|---|-------|
| F1 | Interceptor central único: todo 401 `TOKEN_EXPIRADO` → refresh → reintento **una sola vez**. Segundo 401 → logout. |
| F2 | Sin refresh concurrente: las peticiones en vuelo esperan a que termine el refresh en curso (mutex/cola del interceptor). |
| F3 | Logout en: refresh fallido, respuesta `REFRESH_INVALIDO`, o cierre de sesión del usuario. Siempre se llama `/auth/logout` si hay tokens. |
| F4 | Rutas protegidas: guard de routing exige sesión activa; sin ella → login (routing protegido, req 0-2). |

---

## 3. Convenciones API REST

### 3.1 Versionado

- Prefijo obligatorio: **`/api/v1/...`**. Ningún endpoint fuera de versión.
- Ruptura de contrato → `/api/v2/...`; `v1` se mantiene en deprecación anunciada (no se rompe silenciosamente).
- Recursos en plural, español consistente con el dominio: `/api/v1/productos`, `/api/v1/fiados`, `/api/v1/proveedores`.

### 3.2 Formato de errores JSON (uniforme, todo el API)

```json
{
  "error": {
    "codigo": "RECURSO_NO_ENCONTRADO",
    "mensaje": "El producto solicitado no existe en esta tienda.",
    "detalles": [
      { "campo": "id", "problema": "UUID inexistente" }
    ],
    "request_id": "req-8f14e45f"
  }
}
```

| Campo | Regla |
|-------|-------|
| `codigo` | `SCREAMING_SNAKE_CASE`, de un catálogo cerrado (tabla inferior); el frontend decide comportamientos por código, no por texto |
| `mensaje` | Español, orientado al usuario final, sin jerga técnica |
| `detalles` | Opcional; array de problemas concretos (ej: validación por campo) |
| `request_id` | Correlación con logs del backend (obligatorio en 5xx) |

#### Catálogo base de códigos

| HTTP | Código | Cuándo |
|------|--------|--------|
| 400 | `SOLICITUD_INVALIDA` | Request malformado |
| 401 | `TOKEN_AUSENTE` / `TOKEN_EXPIRADO` / `TOKEN_INVALIDO` / `CREDENCIALES_INVALIDAS` / `REFRESH_INVALIDO` / `REFRESH_EXPIRADO` | Sesión/auth |
| 403 | `PERMISO_INSUFICIENTE` | Token válido, sin permiso para el recurso |
| 404 | `RECURSO_NO_ENCONTRADO` | No existe (o no existe en este tenant) |
| 409 | `CONFLICTO_DATOS` | Ej: código de barras duplicado en el tenant |
| 422 | `VALIDACION_ERROR` | Validación semántica de Pydantic (con `detalles` por campo) |
| 429 | `LIMITE_EXCEDIDO` | Rate limiting |
| 500 | `ERROR_INTERNO` | Falta no controlada (con `request_id`) |

> Nota: un 404 por recurso ajeno al tenant devuelve 404 (no 403) para no filtrar existencia de datos entre tenants.

### 3.3 Paginación

Request (query params):

| Parámetro | Default | Regla |
|-----------|---------|-------|
| `page` | 1 | ≥ 1 |
| `page_size` | 20 | 1–100 |

Response (envoltorio obligatorio en listas):

```json
{
  "items": [ ... ],
  "paginacion": {
    "page": 1,
    "page_size": 20,
    "total": 137,
    "total_pages": 7
  }
}
```

Todo endpoint de listado usa este envoltorio — el frontend no admite arrays crudos.

### 3.4 Reglas transversales

| Tema | Regla |
|------|-------|
| Idioma | Nombres de campos en español consistente con el dominio (`precio_bs`, `fecha_pago`, `abono`) |
| Fechas | ISO 8601 UTC en JSON: `2026-09-03T14:22:00Z` |
| Monedas | Valores numéricos (float/decimal serializado); formateo con tasa BCV es responsabilidad del frontend |
| CORS | Solo orígenes del frontend declarados por Alfredo en el compose; sin `*` |
| Content-Type | `application/json` en request y response |
| Ids | UUID v4 |

---

## Checklist de conformidad (Nelson y Noris)

- [ ] Login/refresh/logout implementados según §2 (duraciones finales documentadas aquí tras F0-04).
- [ ] Todo endpoint usa `/api/v1` y el formato de errores del catálogo (§3.2).
- [ ] Toda lista usa el envoltorio de paginación (§3.3).
- [ ] Frontend: interceptor único, reintento único, mutex de refresh, sin tokens en storage.
- [ ] Aislamiento de tenant derivado del token, jamás de parámetros de request.
- [ ] Toda desviación de este contrato fue acordada bilateralmente y documentada.

## Cambios a este contrato

Este documento es el contrato vivo. Cualquier cambio requiere: (1) acuerdo Nelson + Noris, (2) actualización de este archivo en el mismo PR que el código, (3) reporte de observación a Cristian si el cambio altera tareas de la MAT.
