# BodegApp — Orden de Remediación ST-02 (QA-ST02-01/02 + N-F101-02)

> **Emisor:** Cristian (Project Director)
> **Fecha:** 05/09/2026
> **Destinatarios:** Nelson (Backend) — SR-02 · Alfredo (DevOps) — SR-03
> **Referencia:** Informe ST-02 de Emilio (QA) — ✅ VERIFICADO 7/7, 4 hallazgos no bloqueantes
> **Prioridad:** ALTA — QA-ST02-01 condiciona el deploy a producción (no el staging ni el merge ya ejecutado)

---

## SR-02 · Nelson (Backend) — Remediación QA-ST02-01: Rotación de Refresh Token

### Diagnóstico verificado por Cristian

La rotación de refresh token **ya está implementada** en `backend/app/services/auth_service.py:162-194` (creación de sucesor, marca `rotated_to_id`, revocación del anterior, detección de robo por reuso de cadena). El defecto es de **configuración**: `settings.refresh_rotation_enabled` está deshabilitado por defecto, y el comentario del código (línea 163) lo explica: *"Frontend today keeps the old contractor token (apiClient.ts:81-87)"* — el frontend de Noris aún no persiste el refresh token rotado.

### Alcance

| # | Acción | Detalle |
|---|---|---|
| 1 | Habilitar rotación por defecto | `refresh_rotation_enabled=True` en la configuración del backend (default del setting) |
| 2 | Ajustar frontend (coordinado con Noris vía contrato) | `apiClient.ts:81-87` debe persistir el refresh token rotado devuelto por `/auth/refresh` — el patrón ya existe en la remediación QA-F04-03 (Noris lo implementó en F0-05) |
| 3 | Tests | Test de rotación efectiva: refresh → nuevo RT con jti distinto + RT anterior rechazado (reuso → revocación de cadena) |
| 4 | Rama | `fix/qa-st02-01-rotacion-rt` desde main (worktree nuevo o el de F1-01 si preferís) |
| 5 | Commit convencional | "fix(auth): QA-ST02-01 — habilita rotación de refresh token por defecto (autor: Nelson, Backend)" |

> **Nota de gobernanza:** el punto 2 toca frontend — si preferís limitar tu alcance al backend, reportalo y derivo el ajuste de `apiClient.ts` a Noris como micro-tarea. El backend NO debe esperar al frontend para habilitar el default: el contrato de respuesta ya incluye el refresh_token rotado.

## SR-03 · Alfredo (DevOps) — Remediación QA-ST02-02 + N-F101-02: CSP y Dependencias

### Alcance

| # | Acción | Detalle |
|---|---|---|
| 1 | CSP `font-src` | Agregar `data:` a `font-src` en `infra/docker/proxy/nginx.conf` (header CSP) — desbloquea los 3 subsets Plus Jakarta Sans embebidos como data: |
| 2 | CSP `script-src` | Agregar hash `'sha256-VnGaeq5p8o7gdDBYK87xXJc51jkRwRO9pViRL5bDNbc='` al script inline anti-FOUC de index.html (o eliminar el inline script del build) |
| 3 | Verificación pyjwt (N-F101-02) | Verificar que la imagen Docker de la API no tenga el paquete PyPI `jwt` sombreando a `PyJWT` (hallazgo de Nelson en entorno local de test: `jwt` 1.4.0 causa `AttributeError: jwt.encode`) — fijar `pyjwt[crypto]` explícito en requirements si hace falta |
| 4 | Redeploy staging | Tras SR-02 (rotación habilitada): redeploy del staging con la config nueva para que el inversor vea la rotación activa |
| 5 | Rama | `fix/qa-st02-02-csp` desde main (worktree f0-02-bt-hardening disponible) |
| 6 | Commit convencional | "fix(infra): QA-ST02-02 — CSP font-src data: + hash script inline; pyjwt explícito (autor: Alfredo, DevOps)" |

## Reglas comunes

1. Todo hallazgo con formato obligatorio (ref, descripción con ubicación, severidad, acción, ¿bloquea producción?).
2. NO pushear a main — merge requiere QA de Emilio y autorización exclusiva de Cristian.
3. Fecha límite: **08/09/2026** para ambas remediaciones (antes del deploy a producción, que sigue planificado para diciembre con gates F4-01/F4-02).

---

*Registrado en `docs/MATRIZ-ASIGNACION.md` (SR-02/SR-03) — emitido por Cristian (Project Director), BodegApp 05/09/2026.*
