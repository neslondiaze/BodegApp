# BodegApp — Delegación Formal: Deploy Staging Online

> **Emisor:** Cristian (Project Director)
> **Fecha:** 05/09/2026
> **Destinatario:** Alfredo (DevOps, Célula Díaz Tech)
> **Referencia:** Autorización del inversor — Opción A (Staging/Demo online), sesión 05/09/2026
> **Prioridad:** 🔴 CRÍTICA — directiva del inversor: puesta online INMEDIATA
> **Nueva referencia de tarea:** ST-01

---

## ⚠️ ACTUALIZACIÓN URGENTE (05/09/2026 — misma fecha, directiva del inversor)

El inversor notificó que **la puesta online es de inmediato**. La fecha límite original del 08/09 queda SIN EFECTO: ST-01 vence **HOY 05/09/2026**. Si algún elemento del alcance (ej. mecanismo de acceso restringido) impide el deploy hoy, desplegá primero lo esencial y reportá el delta inmediatamente — no detengas el deploy por perfeccionismo.

## 1. Objetivo

Desplegar el stack completo de BodegApp en un entorno **staging online** con acceso restringido, para que el inversor pueda ver avance tangible del sistema. **NO es producción**: base de datos de prueba, sin datos reales de bodegas.

## 2. Alcance técnico

| Elemento | Especificación |
|----------|----------------|
| Stack | `infra/docker/docker-compose.yml` vigente (API, Frontend, PostgreSQL, proxy Zero Trust) |
| TLS | Certificados de dev (mkcert/CA interna) — válidos para staging, NO para producción |
| Acceso restringido | Basic auth en proxy O túnel privado (cloudflared, patrón ya usado en Atheneia) — a tu criterio técnico, reportá la elección |
| Base de datos | Datos de prueba únicamente — sin datos reales ni PII |
| Secrets | Provisión completa según `infra/docker/README.md` (postgres_password, jwt keys, proxy TLS) con modo 0600 |
| BT-01 incluido | Crear `.dockerignore` en `frontend/` y `backend/` ANTES del build — evita arrastrar node_modules a la imagen |
| BT-02 incluido | chmod 0600 en todos los secrets file-based del host de staging |

> Nota: BT-01 y BT-02 se incluyen aquí porque son baratos y dejan el staging limpio desde el arranque. La remediación completa BT-03..06 sigue en tu encargo formal F0-02 (recordatorio ya emitido).

## 3. Instrucciones de ejecución

1. **Lectura previa:** `infra/docker/README.md` (provisión de secrets), `infra/docker/docker-compose.yml`, `docs/MATRIZ-ASIGNACION.md` (ST-01).
2. **Cambios en archivos** (`.dockerignore`, ajustes de proxy si aplica): en tu worktree `BodegApp-worktrees/f0-02-bt-hardening`, rama `feature/f0-02-bt-alfredo`. El merge a `main` requiere QA de Emilio.
3. **Operación del deploy** (provisión de secrets en host, `docker compose up`, verificación de healthchecks): ejecutala directamente en el host de staging — es operación DevOps, no requiere rama.
4. **Criterio de éxito:** los 4 servicios healthy (healthchecks del compose) + login funcional end-to-end vía el acceso restringido.
5. **Reporte:** URL/acceso del staging + evidencia de healthchecks + elección de mecanismo de restricción. Cualquier hallazgo con el formato obligatorio (ref, descripción, severidad, acción, ¿bloquea producción?).

## 4. Coordinación

- **Emilio (QA):** al declarar el deploy operativo, Cristian derivará smoke test post-deploy (ST-02) — login, refresh, logout, dashboard sobre el staging online.
- **Monitor_Agent (Blue Team):** el staging queda bajo vigilancia de logs desde el primer despliegue (T-05).

## 5. Fecha límite

**HOY 05/09/2026 (INMEDIATO)** — directiva del inversor. ST-02 (smoke test de Emilio) se ejecuta apenas reportes el deploy operativo.

## 6. Protocolo de escalamiento

Bloqueo → marcar ST-01 🟠 en `docs/MATRIZ-ASIGNACION.md` con nota de quién traba + reporte inmediato a Cristian.

---

*Registrado en `docs/MATRIZ-ASIGNACION.md` (ST-01/ST-02) — emitido por Cristian (Project Director), BodegApp 05/09/2026.*
