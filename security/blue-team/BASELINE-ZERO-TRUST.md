# BASELINE-ZERO-TRUST.md — Checklist de Auditoría Sentinel Shield v1.0

> **Blue Team (Sentinel Shield) — Lead_Blue**
> Proyecto: BodegApp | Ref: F0-07 (ajustada por Cristian, modo paralelo autorizado por inversor)
> Objeto de auditoría: `infra/docker/docker-compose.yml` y artefactos asociados (Dockerfiles, nginx.conf, scripts de init, .env.example) producidos por Alfredo (DevOps, F0-02).
> Versión: 1.0 | Fecha: 03/09/2026 | Clasificación: Uso interno — Equipo de Seguridad

---

## 1. Propósito y Alcance

Este documento define el **baseline de seguridad Zero Trust** contra el cual se auditará la entrega del docker-compose endurecido (req 0-4, REQUERIMIENTOS.md). Bajo el ajuste autorizado, Alfredo construye en paralelo; **este baseline es el criterio de aceptación previo a toda aprobación**. La auditoría se ejecutará en dos pasadas:

- **Pasada 1 — Diseño estático**: revisión del YAML, Dockerfiles y configuraciones (antes del primer `docker compose up`).
- **Pasada 2 — Runtime**: verificación con `docker inspect`, `ss -tlnp`, `capsh` y pruebas de conexión entre redes una vez desplegado.

**Alcance**: servicios API (FastAPI), Frontend (React/Vite servido por nginx), PostgreSQL, proxy/nginx, redes Docker, secrets, y todo artefacto en `infra/docker/`.

**Fuera de alcance** (se auditarán en F4-02 o en sus propias refs): código de aplicación backend/frontend (salvo los puntos de verificación multi-tenant y JWT de §8/§9), microservicio operational-stream (Fase 3, red-team F4-01).

### 1.1 Sistema de veredictos

| Veredicto | Significado |
|-----------|-------------|
| ✅ CUMPLE | Evidencia verificada en diseño o runtime |
| 🟡 PARCIAL | Implementado parcialmente o sin evidencia suficiente |
| ❌ NO CUMPLE | Ausente o contradictorio con el baseline |
| N/A | No aplica a esta entrega (justificar) |

**Regla de severidad**: un ítem marcado ❌ con severidad CRÍTICA bloquea la aprobación del diseño. Todo hallazgo se reporta con el formato obligatorio (Ref, Descripción, Severidad, Acción sugerida, ¿Bloquea producción?) — directriz del inversor.

---

## 2. BT-01 — Segmentación de Redes (Zero Trust Network)

**Principio Zero Trust**: ningún servicio es confiable por ubicación de red. La red interna NO es zona de confianza: cada servicio solo ve lo que explícitamente se le autoriza.

| ID | Requisito | Severidad | Método de verificación |
|----|-----------|-----------|------------------------|
| BT-01.01 | El proxy/nginx es el **único** servicio con puertos publicados al host (80/443) | CRÍTICA | Diseño: solo `ports:` en proxy. Runtime: `ss -tlnp` en host — ningún otro listener de Docker |
| BT-01.02 | **Ningún** servicio usa `network_mode: host` | CRÍTICA | `grep -n "network_mode" docker-compose.yml` → 0 resultados |
| BT-01.03 | API **sin puertos directos** al host (sin `ports:`, solo `expose:` o nada) | CRÍTICA | Sin mapeos `ports` en api. Runtime: `curl http://localhost:8000` desde host debe FALLAR |
| BT-01.04 | PostgreSQL **sin puertos directos** al host | CRÍTICA | Ídem BT-01.03. `psql -h localhost` desde host debe FALLAR |
| BT-01.05 | Redes separadas y explícitas: mínimo `frontend` (proxy↔frontend, proxy↔api) y `backend` (api↔db), con `internal: true` donde aplique | ALTA | Análisis del bloque `networks:` por servicio |
| BT-01.06 | PostgreSQL está **solo** en la red backend — nunca comparte red con el proxy | CRÍTICA | Matriz de adyacencia de redes por servicio |
| BT-01.07 | El frontend estático solo comparte red con el proxy (no con api/db directamente) | MEDIA | Ídem análisis de redes |
| BT-01.08 | Default deny implícito: servicios declarados explícitamente en redes; sin red `default` compartida por omisión | ALTA | Docker crea `default` si se omite; verificar que TODOS los servicios declaren sus redes |
| BT-01.09 | Sin `links:` (deprecated) ni `expose:` innecesario a redes no consumidoras | BAJA | Inspección YAML |
| BT-01.10 | Egress control: API necesita salida a internet SOLO para scraping BCV (M-10, `www.bcv.org.ve:443`) — documentar y restringir el razonamiento de salida | ALTA | Revisar si la red de api es `internal: false` justificado; recomendar alias DNS/firewall o proxy de salida cuando exista |

**Matriz de flujo esperado** (autoridad de referencia):

```
Host/Internet ──> proxy (80/443)          [única entrada]
proxy         ──> frontend (estático)
proxy         ──> api (8000, interno)
api           ──> db (5432, interno)
api           ──> https://www.bcv.org.ve (443, salida única documentada)
db            ──> (nadie más)
frontend      ──> (nadie más)
```

Todo flujo fuera de esta matriz = hallazgo.

---

## 3. BT-02 — Gestión de Secrets

| ID | Requisito | Severidad | Método de verificación |
|----|-----------|-----------|------------------------|
| BT-02.01 | Uso de **Docker Secrets** (o equivalente: mounted file, no `environment:`) para: `POSTGRES_PASSWORD`, credenciales DB de la app, claves JWT privadas, secretos de sesión | CRÍTICA | `grep -n "environment" docker-compose.yml` → ninguna clave sensible en texto plano |
| BT-02.02 | **Cero** secrets en variables de entorno planas visibles con `docker inspect` | CRÍTICA | `docker inspect <contenedor>` — sección Env no debe contener contraseñas/tokens |
| BT-02.03 | **Cero** claves/credenciales quemadas (`hardcoded`) en Dockerfiles, imágenes o scripts de init | CRÍTICA | Revisión de todos los Dockerfiles, entrypoints y scripts en `infra/docker/` |
| BT-02.04 | Clave privada JWT RS256 montada como secret con permisos restringidos (0400/0600, uid del proceso) y **nunca** copiada al build context ni a la imagen | CRÍTICA | Revisar `.dockerignore`, Dockerfiles y volumen del secret |
| BT-02.05 | Archivo `.env` NO versionado en git (`.gitignore` lo cubre) y solo usado para variables no sensibles (imagen, tag, dominio) | ALTA | `git ls-files \| grep -i env` → 0; revisar `.gitignore` |
| BT-02.06 | Existe `.env.example` o documentación de variables SIN valores reales | MEDIA | Presencia del archivo con placeholders |
| BT-02.07 | Volumen de secrets no listado en imágenes (`docker history --no-trunc` sin strings sensibles) | ALTA | Inspección de capas de imagen |
| BT-02.08 | Rotación documentada: cómo se rota la contraseña de DB y las claves JWT sin rebuild de imagen | MEDIA | Documento o comentario en compose |
| BT-02.09 | Base de datos: `POSTGRES_PASSWORD` vía secret; usuario de app distinto del superusuario (ver BT-04) | CRÍTICA | Cruce con BT-04.01 |

---

## 4. BT-03 — Hardening de Contenedores

| ID | Requisito | Severidad | Método de verificación |
|----|-----------|-----------|------------------------|
| BT-03.01 | `user:` no-root en TODOS los servicios (uid/gid numérico, no solo nombre) | CRÍTICA | `docker inspect --format '{{.Config.User}}'` ≠ root/0 |
| BT-03.02 | `read_only: true` en sistema de archivos raíz de todos los contenedores (con `tmpfs` explícito para /tmp y paths de escritura necesarios) | ALTA | `docker inspect` → Rootfs readonly; runtime write test |
| BT-03.03 | `cap_drop: [ALL]` como base; solo se agregan caps con justificación documentada | ALTA | `docker inspect --format '{{.HostConfig.CapDrop}}'` |
| BT-03.04 | `security_opt: [no-new-privileges:true]` en todos los servicios | ALTA | Inspección `SecurityOpt` |
| BT-03.05 | **Sin** `privileged: true` en ningún servicio | CRÍTICA | `grep -n "privileged" docker-compose.yml` |
| BT-03.06 | Resource limits: `mem_limit`/`cpus` (o `deploy.resources`) por servicio | MEDIA | Inspección compose; sugerencia: api 512m/1.0, db 1g/1.5, proxy 128m/0.5 como punto de partida |
| BT-03.07 | `restart: unless-stopped` o `on-failure` (no `always` ciego; no `no`) | BAJA | Inspección compose |
| BT-03.08 | `healthcheck` definido en api (HTTP con curl/wget a endpoint salud), db (`pg_isready`), proxy y frontend | ALTA | Inspección compose + `docker ps` muestra healthy |
| BT-03.09 | Imágenes: tag pinado por digest o versión exacta (no `:latest`) | ALTA | Inspección `image:` en compose |
| BT-03.10 | Volúmenes declarados explícitamente; sin binds amplios del host (`/:/...` o `$HOME`) | ALTA | Inspección `volumes:` |
| BT-03.11 | `tmpfs` con `noexec,nosuid,nodev` donde se monte /tmp | MEDIA | Inspección flags de tmpfs |
| BT-03.12 | Logging: driver json-file con límite de tamaño/rotación (`max-size`, `max-file`) o driver externo | MEDIA | Inspección `logging:` |
| BT-03.13 | `stop_grace_period` corto (≤10s) para api/db; PID 1 maneja SIGTERM (init/tini si el proceso no lo hace) | BAJA | Inspección compose + Dockerfile ENTRYPOINT |
| BT-03.14 | Sin `hostPath` de socket Docker montado (`/var/run/docker.sock`) en ningún contenedor | CRÍTICA | `grep -n "docker.sock" docker-compose.yml` |

---

## 5. BT-04 — Hardening de PostgreSQL

| ID | Requisito | Severidad | Método de verificación |
|----|-----------|-----------|------------------------|
| BT-04.01 | Usuario de la app **no-superuser** (rol dedicado `bodegapp_app`): `NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT` con solo GRANT necesarios (CONNECT, USAGE schema, DML en tablas de la app) | CRÍTICA | Script de init SQL: verificar roles y grants; runtime: `\du` y prueba de acciones prohibidas |
| BT-04.02 | Superusuario `postgres` solo para bootstrap/migraciones iniciales; la app NUNCA se conecta con él | CRÍTICA | Revisar `DATABASE_URL` que consume la api |
| BT-04.03 | `POSTGRES_DB` y usuarios creados vía init scripts (montados en `/docker-entrypoint-initdb.d/`) | MEDIA | Inspección volúmenes/scripts |
| BT-04.04 | Volumen de datos con nombre (no anonymous), respaldo documentado (backup plan) | MEDIA | Inspección compose + doc de operación |
| BT-04.05 | Sin exposición al host (cruce con BT-01.04) y sin `POSTGRES_PASSWORD` en env plano (cruce con BT-02) | CRÍTICA | Cruce obligatorio en informe |
| BT-04.06 | Parámetros de conexión: `max_connections` razonable; timeout de conexión/idle; SSL interno entre api↔db si el orquestador lo soporta ( TLS obligatorio en producción cloud) | BAJA (local) / ALTA (cloud) | `postgresql.conf` o `command:` args |
| BT-04.07 | Log de conexiones y errores habilitado (`log_connections`, `log_disconnections` en producción solo si el volumen lo tolera; mínimo `log_min_error_statement=error` sin parámetros de valores) | BAJA | Config PG |
| BT-04.08 | Estrategia multi-tenant (pendiente de Nelson, F0-03: schema-por-tenant vs RLS) NO comprometida por el diseño de red: el usuario de app no debe ser owner del schema con derechos ilimitados si se adopta RLS | ALTA | Coordinación F0-03 ↔ F0-02; revisar grants vs estrategia elegida |

---

## 6. BT-05 — Hardening de nginx / Proxy

| ID | Requisito | Severidad | Método de verificación |
|----|-----------|-----------|------------------------|
| BT-05.01 | Security headers obligatorios: `Strict-Transport-Security` (HSTS), `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY` (o `frame-ancestors 'none'`), `Referrer-Policy: strict-origin-when-cross-origin`, `Content-Security-Policy` (mínima restrictiva por defecto), `Permissions-Policy` restrictiva | ALTA | `curl -I` contra proxy en runtime; revisión nginx.conf |
| BT-05.02 | TLS: solo TLS 1.2+ (1.3 preferente); suites fuertes; certificados montados vía secret/volumen (no en imagen); redirección 80→443 en producción | CRÍTICA (prod) / ALTA (dev) | `openssl s_client` / `nmap --script ssl-enum-ciphers` |
| BT-05.03 | Rate limiting: `limit_req` por IP para endpoints de login/refresh; `limit_conn` general | ALTA | nginx.conf + prueba de ráfaga (ej. 50 req/s → 429/503) |
| BT-05.04 | Timeouts explícitos y acotados: `client_body_timeout`, `send_timeout`, `proxy_read_timeout`, `keepalive_timeout` (sugerido: 30–60s, no defaults infinitos) | MEDIA | Revisión nginx.conf |
| BT-05.05 | Tamaños de cuerpo limitados: `client_max_body_size` (ej. 2m salvo justificación de carga de imágenes) | MEDIA | Revisión nginx.conf |
| BT-05.06 | Server tokens off (`server_tokens off`) | BAJA | `curl -I` — header Server sin versión |
| BT-05.07 | Sin `ssl on` deprecated; `ssl_protocols` sin SSLv3/TLS1.0/1.1; `ssl_prefer_server_ciphers on` | ALTA | Config + escaneo |
| BT-05.08 | Rutas de proxy acotadas: `location /api/` → api interna; sin catch-all de puertos arbitrarios; sin exposición de `/docs` ni `/openapi.json` de FastAPI en producción (o protegidos) | ALTA | Revisión nginx.conf + prueba HTTP |
| BT-05.09 | WebSockets: si se prepara para operational-stream (Fase 3), `proxy_http_version 1.1` + `Upgrade` headers YA definidos de forma segura | BAJA (ahora) | Revisión nginx.conf |
| BT-05.10 | Logging de nginx con formato estructurado (json o combined+) incluyendo `$request_time` y `$status` | MEDIA | Revisión access_log format |

---

## 7. BT-06 — Autenticación JWT RS256 (puntos de verificación de compose + config)

> El diseño JWT completo es de Nelson (F0-04). Aquí fijo los requisitos de seguridad que el compose/config debe garantizar y los que auditaré en código cuando llegue.

| ID | Requisito | Severidad | Método de verificación |
|----|-----------|-----------|------------------------|
| BT-06.01 | Clave **privada** RS256 solo accesible al servicio api, montada como secret (file) con permisos mínimos; JAMÁS en imagen, env, ni accesible a proxy/frontend/db | CRÍTICA | Cruce BT-02.04 + `docker inspect` de montajes por servicio |
| BT-06.02 | Clave **pública** distribuida a los verificadores (proxy si valida, frontend solo vía endpoint JWKS si aplica); nunca la privada | ALTA | Inspección de qué secrets monta cada servicio |
| BT-06.03 | Verificación de algoritmo por **lista blanca**: el validador debe fijar `algorithms=["RS256"]` — rechazo explícito de `none`, `HS256` en claves RSA (confusion attack) y de algoritmos no declarados. El header `alg` del token NO es fuente de confianza | CRÍTICA | Revisión de config de validación (código F0-04) + prueba con token HS256 firmado con la pública |
| BT-06.04 | Expiración: access token corto (≤15 min recomendado), refresh token con expiración y rotación; verificación de `exp` SIEMPRE activa (sin `verify_exp=False`) | ALTA | Revisión de configuración JWT + pruebas |
| BT-06.05 | Validación completa de claims: `iss`, `aud`, `exp`, `nbf` — sin "decode sin verify" en NINGÚN punto del código (frontend incluido: decodificar ≠ validar) | ALTA | Revisión de código (punto de chequeo para F0-04/F0-05) |
| BT-06.06 | Tokens dual (contratante/trabajo, req 0-2): claim de tipo de token distinguible e inintercambiable; un token de trabajo NO debe poder usarse como contratante y viceversa | CRÍTICA | Revisión F0-04: claim `typ`/`scope` verificado en cada endpoint |
| BT-06.07 | Kid/keyId en headers de token para rotación de claves; JWKS endpoint si hay verificación externa | BAJA | Revisión F0-04 |
| BT-06.08 | Denegación por omisión: tokens sin tenant claim → rechazados (cruce multi-tenant §8) | ALTA | Revisión F0-04 |

---

## 8. BT-07 — Multi-Tenant: Puntos de Verificación de Aislamiento (revisión de código)

> Estrategia a decidir por Nelson (F0-03). El baseline exige verificación en CUALQUIER estrategia elegida. La auditoría de código aplicará en F1-01.. y F4-02.

| ID | Punto de verificación | Severidad |
|----|----------------------|-----------|
| BT-07.01 | **Filtro de tenant obligatorio en TODA consulta**: cada query filtra por `tenant_id` (o su equivalente RLS/schema). Prohibido un endpoint de listado sin escoping de tenant | CRÍTICA |
| BT-07.02 | **Sin IDs secuenciales globales exfiltrables entre tenants**: usar UUIDs o IDs compuestos (tenant+id) para que un tenant no enumere recursos de otro | ALTA |
| BT-07.03 | **RLS (si se adopta)**: `SET app.tenant_id`/contexto por sesión/transaction; el usuario de app NO es BYPASSRLS; prueba automatizada: tenant A consultando ID de tenant B → 0 filas | CRÍTICA |
| BT-07.04 | **Schema-por-tenant (si se adopta)**: switch de schema con búsqueda estricta contra whitelist (sin concatenación de strings → inyección de schema); tenant inexistente → error, no fallback a public | CRÍTICA |
| BT-07.05 | El tenant se deriva del **token JWT verificado**, nunca de un parámetro de request (query/body) confiable del cliente | CRÍTICA |
| BT-07.06 | Cross-tenant por FK: FKs solo dentro del mismo tenant o global de solo lectura (catálogos compartidos documentados) | ALTA |
| BT-07.07 | Migraciones/Alembic: herramientas de admin operan con tenant explícito; sin endpoints de app que expongan tenants cruzados | ALTA |
| BT-07.08 | Respuestas de error no filtran existencia de recursos de otros tenants (enumeración por mensaje diferencial) | MEDIA |
| BT-07.09 | Tests de aislamiento: suite obligatoria de casos "tenant A vs tenant B" (cross-lease) en QA (coordinar con Emilio F1-09) | ALTA |
| BT-07.10 | Datos de telemetría/logs no mezclan tenant_id en mensajes de error hacia cliente | MEDIA |

---

## 9. BT-08 — Ciclo de Vida del Secret y del Despliegue

| ID | Requisito | Severidad |
|----|-----------|-----------|
| BT-08.01 | Documento de operación: cómo generar secrets iniciales (comandos reproducibles con openssl/rand), dónde viven, quién los rota | ALTA |
| BT-08.02 | Backup del volumen de DB y de secrets documentado con custodia (NO en el repo) | ALTA |
| BT-08.03 | `docker compose config` valida sin warnings de secrets/vars obsoletas | BAJA |
| BT-08.04 | No hay SSH ni herramientas de shell (curl, wget) innecesarias en imágenes de runtime (multi-stage build) | MEDIA |
| BT-08.05 | Escaneo de imágenes (trivy/grype) ejecutado antes de aprobar; sin CVEs CRÍTICOS/exploitables sin remediar | ALTA |

---

## 10. Criterios de Aprobación

**APROBADO** cuando:
1. 0 ítems ❌ con severidad CRÍTICA en BT-01..BT-06 (diseño y runtime).
2. ≤3 ítems 🟡 PARCIAL en total, cada uno con plan de cierre fechado con Alfredo.
3. Matriz de flujos de red (§2) verificada en runtime sin desviaciones.
4. Informe de auditoría emitido en `security/blue-team/` con el formato obligatorio.

**CONDICIONADO** (aprobación con observaciones): hallazgos ALTA con plan de cierre. **RECHAZADO**: cualquier CRÍTICA sin plan inmediato.

---

## 11. Registro de Auditoría (se completa al recibir la entrega F0-02)

| Sección | ✅ CUMPLE | 🟡 PARCIAL | ❌ NO CUMPLE | N/A | Veredicto |
|---------|-----------|------------|--------------|-----|-----------|
| BT-01 Redes | — | — | — | — | Pendiente |
| BT-02 Secrets | — | — | — | — | Pendiente |
| BT-03 Contenedores | — | — | — | — | Pendiente |
| BT-04 PostgreSQL | — | — | — | — | Pendiente |
| BT-05 Proxy | — | — | — | — | Pendiente |
| BT-06 JWT | — | — | — | — | Pendiente |
| BT-07 Multi-tenant (código) | — | — | — | — | Pendiente (F0-03/F0-04) |
| BT-08 Ciclo de vida | — | — | — | — | Pendiente |

> Estado: ⏳ En espera de entrega de F0-02 (Alfredo, deadline 10/09/2026). Auditar en ≤24h de recibida.
