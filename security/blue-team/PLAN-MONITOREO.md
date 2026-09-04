# PLAN-MONITOREO.md — Vigilancia Monitor_Agent desde el Primer Despliegue

> **Blue Team (Sentinel Shield) — Lead_Blue**
> Proyecto: BodegApp | Ref: F0-07 (ajustada) + T-05 (MAT transversal)
> Versión: 1.0 | Fecha: 03/09/2026 | Clasificación: Uso interno — Equipo de Seguridad

---

## 1. Propósito

Define qué vigilará **Monitor_Agent** desde el primer `docker compose up` (entorno de desarrollo de Alfredo, F0-02) hasta producción (F4-06). Objetivo: detección temprana de (1) fallos de seguridad, (2) anomalías operativas, (3) abuso de autenticación, (4) degradación del scraping BCV — con base en el baseline `BASELINE-ZERO-TRUST.md`.

**Cobertura por fases**:

| Fase | Alcance del monitoreo |
|------|----------------------|
| F0 (primer despliegue) | Infraestructura: contenedores, redes, logs de arranque, healthchecks |
| F1 | + CRUDs multi-tenant, errores de aplicación, aislamiento (eventos de cross-tenant) |
| F2 | + Auth en producción real (login fallidos, tokens), scraping BCV, fiados (datos sensibles) |
| F3 | + operational-stream (WebSocket), balanza serial |
| F4 | + Telemetría completa pre-lanzamiento, alimentación al pentest (F4-01) |

---

## 2. Fuentes de Telemetría

| # | Fuente | Contenido esperado | Punto de recolección |
|---|--------|-------------------|----------------------|
| F-01 | `docker events` | start/die/kill/health_status de contenedores | Host Docker (Alfredo) |
| F-02 | Logs de contenedor `api` (stdout) | Accesos HTTP, errores, trazas de auth, query errors | `docker logs` / driver json con rotación (cruce BT-03.12) |
| F-03 | Logs de `db` (PostgreSQL) | Conexiones, errores, deadlocks, duración de queries | stderr PG + log_min_errors |
| F-04 | Logs de `proxy` (nginx) | Access log (IP, status, request_time, user_agent), error log | access_log format (cruce BT-05.10) |
| F-05 | Healthchecks de Docker | Estado `healthy/unhealthy` por servicio | `docker ps` / events |
| F-06 | (Fase 2+) Logs de aplicación estructurados | Eventos de negocio: login, refresh, scraping, alertas | A definir con Nelson (formato JSON structurado) |
| F-07 | (Fase 2+) Métricas BCV | Duración de scraping, resultado, tasa obtenida vs previa | Job de scraping (M-10) |
| F-08 | (F4+) Agente de métricas (Prometheus/Grafana o equivalente ligero) | CPU, memoria, red I/O, latencias | A definir con Alfredo en F4-02 |

> **Requisito estructural temprano (pedir ya a Alfredo/Nelson)**: logs a stdout/stderr con formato JSON una-línea (sin pretty-print) para ingerencia automática; `request_id` propagado api↔proxy.

---

## 3. Eventos a Vigilar y Umbrales de Alerta

### 3.1 Infraestructura (desde F0)

| ID | Evento | Umbral / señal | Severidad | Acción automática sugerida |
|----|--------|----------------|-----------|---------------------------|
| M-IF-01 | Contenedor en estado `unhealthy` o reinicio (`die`+`start` repetido) | ≥3 reinicios en 10 min | ALTA | Alerta + captura de `docker inspect` + últimos 200 líneas de log |
| M-IF-02 | Contenedor OOM-killed (exit 137) | 1 ocurrencia | ALTA | Alerta; revisar limits (BT-03.06) |
| M-IF-03 | Puerto inesperado publicado en el host (nuevo listener) | Cualquiera fuera de 80/443 del proxy | CRÍTICA | Alerta inmediata — posible desviación del baseline BT-01 |
| M-IF-04 | Salud de PostgreSQL: conexiones rechazadas por `max_connections` | ≥5 en 5 min | MEDIA | Alerta; revisar pool de la api |
| M-IF-05 | Disco: volumen de logs/datos >80% | 80% / 90% | MEDIA/ALTA | Alerta + rotación de logs |
| M-IF-06 | Cambio en la topología de red (nueva red, contenedor adjunto a red backend) | Cualquiera no documentado | ALTA | Alerta — cruces con matriz de flujos (BT-01) |

### 3.2 Autenticación y Abuso (desde F2; patrones definidos ya)

| ID | Evento | Umbral | Severidad | Acción |
|----|--------|--------|-----------|--------|
| M-AU-01 | Login fallido por usuario | ≥5 en 5 min (mismo usuario) | MEDIA | Alerta + rate limit verificación (BT-05.03) |
| M-AU-02 | Login fallido por IP (multi-usuario) | ≥10 en 5 min desde misma IP | ALTA | Alerta — posible spraying/credential stuffing |
| M-AU-03 | Token rechazado por firma inválida | ≥3 en 1 min | CRÍTICA | Alerta inmediata — posible ataque de forja o key mismatch; congelar y revisar |
| M-AU-04 | Token rechazado por algoritmo no permitido (`none`/`HS256` en clave RS) | **1 sola ocurrencia** | CRÍTICA | Alerta inmediata + bloqueo temporal de IP — indicio de ataque activo (BT-06.03) |
| M-AU-05 | Refresh token reutilizado (rotación violada) | 1 ocurrencia | ALTA | Alerta — posible robo de token; revocar familia de tokens |
| M-AU-06 | Token de tipo trabajo usado en endpoint de contratante (o viceversa) | 1 ocurrencia | CRÍTICA | Alerta — violación de tokens dual (BT-06.06) |
| M-AU-07 | Uso de token expirado repetido | ≥10 en 10 min (mismo subject) | BAJA | Alerta informativa — cliente desactualizado o probing |
| M-AU-08 | Login exitoso fuera de horario patronal (configurable por tenant) | ≥1 | BAJA | Informativo → escalar si acumula |

### 3.3 Multi-Tenant: Aislamiento (desde F1)

| ID | Evento | Umbral | Severidad | Acción |
|----|--------|--------|-----------|--------|
| M-MT-01 | Query con resultado cross-tenant detectado en test automático (canary) | 1 ocurrencia | CRÍTICA | Alerta + bloqueo del endpoint implicado + revisión inmediata con Nelson |
| M-MT-02 | Intento de acceso a recurso de otro tenant (403/404 diferencial) | ≥20 en 10 min por usuario/IP | ALTA | Alerta — enumeración de recursos (BT-07.02/07.08) |
| M-MT-03 | Error 500 que incluya datos de otro tenant en mensaje | 1 ocurrencia | CRÍTICA | Alerta + sanitización de mensaje (BT-07.10) |
| M-MT-04 | Creación de schema/tenant fuera del flujo de provisioning | 1 ocurrencia | ALTA | Alerta — revisar con Nelson/Alfredo |

> **Canary de aislamiento (proponer a Emilio, F1-09)**: job periódico que con tenant A intenta leer IDs de tenant B (muestra) y verifica 0 resultados / 403. Resultado → telemetría M-MT-01.

### 3.4 Scraping BCV y Anomalías (desde F2)

| ID | Evento | Umbral | Severidad | Acción |
|----|--------|--------|-----------|--------|
| M-BCV-01 | Scraping fallido (timeout, HTTP != 200, parse error) | 2 consecutivos | ALTA | Alerta; revisar selector/estructura del sitio BCV |
| M-BCV-02 | Tasa obtenida desviada de la última conocida | >10% de variación | ALTA | Alerta — validar manualmente; posible cambio de estructura o valor real anómalo |
| M-BCV-03 | Scraping ejecutado fuera de la programación del tenant (M-13) | 1 ocurrencia | ALTA | Alerta — posible scheduler comprometido o bug |
| M-BCV-04 | Latencia de scraping | >30s | MEDIA | Informativo — degradación del sitio BCV |
| M-BCV-05 | Volumen de peticiones de salida a internet desde api | >X req/hora a dominios no bcv.org.ve | ALTA | Alerta — posible SSRF/exfiltración (cruce BT-01.10) |
| M-BCV-06 | Resultado idéntico repetido N días (tasa congelada) | 5 ejecuciones con mismo valor exacto | BAJA | Informativo — verificar si es comportamiento normal del BCV |

### 3.5 Aplicación y Datos Sensibles (desde F2)

| ID | Evento | Umbral | Severidad | Acción |
|----|--------|--------|-----------|--------|
| M-AP-01 | Error 5xx sostenido en api | >5% de requests en 10 min | ALTA | Alerta + stack trace de los últimos errores |
| M-AP-02 | Latencia p95 de endpoints CRUD | >2s sostenido 15 min | MEDIA | Informativo → optimizar |
| M-AP-03 | Acceso a datos de fiados (M-08/09 — datos personales de deudores) exportado en volumen | ≥500 registros leídos por usuario en 10 min | ALTA | Alerta — posible exfiltración (datos sensibles GDPR/PI, coordinar con Wilfredo F4-03) |
| M-AP-04 | Migraciones ejecutadas fuera de ventana | 1 ocurrencia | MEDIA | Alerta — verificar autoría |
| M-AP-05 | Cambios de configuración de tenant masivos (config de tienda) | ≥10 en 1h | BAJA | Informativo |

---

## 4. Flujo de Respuesta (Monitor_Agent)

```
Evento → Recolección (logs/events) → Regla (umbral §3) → Clasificación (severidad)
  → CRÍTICA: alerta inmediata a Lead_Blue + Cristian (canal definido) + contención sugerida
  → ALTA: alerta a Lead_Blue, respuesta <4h laborables
  → MEDIA: cola diaria de triaje
  → BAJA: informe semanal
```

**Registro**: todo evento M-* que dispare alerta se registra en `security/blue-team/incidentes/` (estructura a crear) con: ID, fecha, regla, evidencia (logs recortados), acción tomada, resolución. Los incidentes CRÍTICOS se reportan a Cristian con el formato obligatorio de hallazgos.

**Coordinación Red Team**: cuando Lead_Red inicie F4-01, las reglas M-AU-03/04/05 y M-BCV-05 alimentan los IOC esperados del pentest; se acuerda ventana y reglas de enfrentamiento para no generar falsos CRÍTICOS operativos.

---

## 5. Requisitos a Otros Agentes (dependencias de monitoreo)

| Ref | Pedido a | Descripción |
|-----|---------|-------------|
| REQ-M1 | Alfredo (F0-02) | Logs a stdout JSON una-línea; `logging` con rotación (BT-03.12); access log nginx estructurado (BT-05.10); exponer `docker events` de lectura al Monitor |
| REQ-M2 | Nelson (F0-04) | Emitir eventos de auth con resultado y motivo (firma inválida / alg no permitido / expirado / tipo incorrecto) SIN logging de tokens completos — solo `jti`/prefijo |
| REQ-M3 | Nelson (F1+) | `request_id` en todas las respuestas y trazas; logs sin PII innecesaria (nombres de fiados, etc.) |
| REQ-M4 | Emilio (F1-09) | Ejecutar canary de aislamiento multi-tenant (M-MT-01) como prueba programada |
| REQ-M5 | Alfredo (F4-02) | Evaluar stack de métricas (Prometheus u otro ligero) con dashboards de las reglas §3 |

---

## 6. Métricas de Eficacia del Monitoreo (KPI)

| KPI | Meta |
|-----|------|
| Falsos positivos en reglas CRÍTICAS | <10% |
| Tiempo medio de detección (MTTD) incidentes ALTA+ | <15 min |
| Tiempo medio de respuesta (MTTR) CRÍTICAS | <1h |
| Cobertura de servicios con logs estructurados | 100% para F2 |

> Revisión de este plan: tras primer despliegue (ajustar umbrales con datos reales), en F2 (activar auth/BCV), y pre-F4-01 (sincronizar con Red Team).
