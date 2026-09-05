# BodegApp — Recordatorio Formal de Arranque

> **Emisor:** Cristian (Project Director)
> **Fecha:** 05/09/2026
> **Destinatario:** Alfredo (DevOps, Célula Díaz Tech)
> **Referencia:** Delegación 04/09/2026 (noche) — autorizada por el inversor
> **Prioridad:** ALTA — BT-01 y BT-02 son condición pre-producción

---

## 1. Motivo del recordatorio

La delegación formal de remediación de observaciones Blue Team (BT-01..BT-06) fue emitida la noche del 04/09/2026. A la fecha, tu worktree asignado (`BodegApp-worktrees/f0-02-bt-hardening`, rama `feature/f0-02-bt-alfredo`) **no registra commits ni archivos modificados**. Este documento constituye el recordatorio formal de arranque.

## 2. Alcance de la tarea

Remediación de las 6 observaciones del gate de seguridad F0-07 (Lead_Blue) sobre el diseño Docker Zero Trust de F0-02. Veredicto original: APROBADO CON OBSERVACIONES — ninguna bloquea producción, pero **BT-01 y BT-02 deben resolverse antes del deploy a producción**.

| Ref | Descripción | Severidad | Acción correctiva | Condición |
|-----|-------------|-----------|-------------------|-----------|
| BT-01 | Sin `.dockerignore` en `frontend/` y `backend/`; `COPY . .` arrastra node_modules al build | Media | Crear .dockerignore en ambos contextos | **Pre-producción** |
| BT-02 | `secrets/postgres_password.txt` con modo 0644 en host (resto 0600) | Media | chmod 0600 + documentar provisión | **Pre-producción** |
| BT-03 | `/tmp` del api sin noexec pese a staging de claves en /tmp/keys | Media | Separar staging a /run/keys noexec | Backlog |
| BT-04 | uvicorn `--forwarded-allow-ips '*'` confía en cualquier peer | Media | Restringir a IP del proxy | Backlog F1 |
| BT-05 | CSP con `style-src 'unsafe-inline'` | Baja | Migrar a nonce (fase posterior) | Backlog |
| BT-06 | Masters arrancan como root antes del drop (patrón documentado) | Baja | Verificar runtime en F0-08 | Backlog (con Emilio) |

> Nota: BT-02 ya cuenta con remediación documental (commit `daee6a5` — política 0600 obligatoria para secrets file-based). La remediación técnica del permiso en host queda incluida en tu alcance.

## 3. Instrucciones de ejecución

1. **Lectura previa obligatoria:** `docs/REQUERIMIENTOS.md`, `docs/MATRIZ-ASIGNACION.md` (registro BT-01..06), `docs/ENCARGOS-SUBAGENTES.md` (reglas), y el diseño en `infra/docker/` (docker-compose.yml, Dockerfile.api, Dockerfile.frontend, proxy/nginx.conf).
2. **Worktree asignado:** `BodegApp-worktrees/f0-02-bt-hardening` — rama `feature/f0-02-bt-alfredo`. Todo tu trabajo se realiza ahí; NO trabajes sobre `main`.
3. **Alcance de archivos:** exclusivamente `infra/docker/` y `.dockerignore` de ambos contextos. No toques código de backend/frontend.
4. **Reporte de observaciones:** cualquier hallazgo durante la remediación se reporta con el formato obligatorio (ref, descripción con ubicación exacta, severidad, acción correctiva, ¿bloquea producción?) — directiva del inversor: todo hallazgo se reporta, sin importar cuán mínimo parezca.
5. **Cierre:** al terminar, reportá a Cristian para derivar a QA (Emilio). El merge a `main` requiere QA aprobado — autorización exclusiva de Cristian.

## 4. Fecha límite

**10/09/2026** (según MATRIZ-ASIGNACION, F0-02 en revisión con observaciones pendientes). BT-01 y BT-02 son condición pre-producción: su retraso impacta directamente el plan de despliegue de F4-06.

## 5. Protocolo de escalamiento

Si encontrás algún bloqueo (dependencia de Nelson, conflicto con el diseño Zero Trust, etc.), marcá la tarea 🟠 en `docs/MATRIZ-ASIGNACION.md` con nota de quién la traba y reportá inmediatamente a Cristian. No esperes a la fecha límite para escalar.

---

*Registro de este recordatorio en `docs/MATRIZ-ASIGNACION.md` — emitido por Cristian (Project Director), BodegApp 05/09/2026.*
