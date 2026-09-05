# BodegApp — Delegación Formal: Smoke Test Post-Deploy (Staging Online)

> **Emisor:** Cristian (Project Director)
> **Fecha:** 05/09/2026
> **Destinatario:** Emilio (QA, Célula Díaz Tech)
> **Referencia:** ST-01 reportado operativo por Alfredo (DevOps) — commit `c6b48ab`, rama `feature/f0-02-bt-alfredo` (sin merge aún)
> **Prioridad:** 🔴 CRÍTICA — el acceso al inversor y el merge de infraestructura a `main` están bloqueados por este gate
> **Referencia de tarea:** ST-02

---

## 1. Objetivo

Ejecutar el **smoke test post-deploy** sobre el staging online de BodegApp y emitir un veredicto formal **✅ VERIFICADO / ❌ RECHAZADO** que habilite (o no) dos entregables críticos:

1. La **entrega del acceso al inversor** (comprometida en RI-001 para hoy, tras este smoke test).
2. La **autorización de merge** de `feature/f0-02-bt-alfredo` a `main` por parte de Cristian.

## 2. Alcance del smoke test

| # | Verificación | Criterio de éxito |
|---|--------------|-------------------|
| 1 | Salud de servicios | 4/4 contenedores healthy (proxy, api, frontend, postgres) |
| 2 | Carga de la SPA | La aplicación carga sin errores de consola ni recursos caídos |
| 3 | Login | Autenticación con usuario demo → emisión de JWT dual-token (contratante/trabajo) |
| 4 | Sesión / refresh | Renovación de token operativa (rotación de refresh token) |
| 5 | Logout | Cierre de sesión con revocación; idempotente en repetición |
| 6 | Dashboard | Renderizado correcto tras login (ruta protegida) |
| 7 | Seguridad básica | Credenciales inválidas → 401 uniforme `CREDENCIALES_INVALIDAS`, sin leak de información |

> **Fuera de alcance:** pruebas funcionales de inventario (Fase 1 aún en desarrollo), performance, y remediaciones BT-03..06 (siguen en F0-02). Este es un smoke test de disponibilidad del camino crítico, no una auditoría profunda.

## 3. Acceso al staging

| Elemento | Detalle |
|---|---|
| URL | `https://192.168.100.122` (también `https://localhost` / `https://127.0.0.1`) |
| Autenticación de borde (basic auth) | Credenciales provistas por Alfredo/Cristian por canal privado — ver `infra/docker/secrets/` en el host de staging (NO versionadas en el repo) |
| Usuario demo de la app | `demo` / `Demo123!` (sembrado según `infra/docker/README.md` §4b) |
| TLS | Certificados de desarrollo (mkcert) — aceptá la advertencia del navegador; es esperado en staging |

## 4. Instrucciones de ejecución

1. **Tarea de SOLO LECTURA sobre el entorno** — no modificás código ni configuración. Si un hallazgo requiere corrección, se reporta y se delega al responsable (Alfredo/Nelson), no lo ejecutás vos.
2. Ejecutá las verificaciones de la sección 2 en orden, documentando evidencia (código HTTP, capturas si aplica).
3. **Reporte obligatorio:** veredicto final VERIFICADO/RECHAZADO + tabla de verificaciones con evidencia + todo hallazgo con el formato obligatorio (ref, descripción con ubicación, severidad, acción correctiva sugerida, ¿bloquea producción?).
4. **Directiva del inversor vigente:** todo hallazgo, por mínimo que parezca, se reporta detalladamente — la decisión de actuar o no la toman Cristian y el inversor.

## 5. Coordinación

- **Alfredo (DevOps):** disponible para desbloqueos del entorno (restart de servicios, logs) si algo falla durante el test.
- **Monitor_Agent (Blue Team):** el staging está bajo vigilancia de logs (T-05) — tu tráfico de prueba queda registrado, es esperado.
- **Cristian:** con tu veredicto VERIFICADO, se ejecuta el merge de infra a `main` y la entrega de acceso al inversor (cierre de RI-001).

## 6. Fecha límite

**HOY 05/09/2026 — INMEDIATO.** El acceso al inversor está prometido para hoy tras este smoke test (RI-001).

## 7. Protocolo de escalamiento

Bloqueo del entorno (servicio caído, credenciales de borde inválidas, etc.) → marcar ST-02 🟠 en `docs/MATRIZ-ASIGNACION.md` con nota de quién traba + reporte inmediato a Cristian.

---

*Registrado en `docs/MATRIZ-ASIGNACION.md` (ST-02) — emitido por Cristian (Project Director), BodegApp 05/09/2026.*
