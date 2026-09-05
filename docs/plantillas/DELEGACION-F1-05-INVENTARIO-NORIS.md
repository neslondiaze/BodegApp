# BodegApp — Delegación Formal: Pantallas de Inventario — Arranque Parcial (M-01)

> **Emisor:** Cristian (Project Director)
> **Fecha:** 05/09/2026
> **Destinatario:** Noris (Frontend, Célula Díaz Tech)
> **Referencia:** Directiva del inversor — flujo continuo entre fases (máxima prioridad)
> **Prioridad:** 🔴 ALTA — la API de Tienda (F1-03) ya está construida; no esperás a los demás CRUDs
> **Referencia de tarea:** F1-05 (arranque parcial — pantalla Configuración de Tienda)

---

## 1. Objetivo

Arrancar **F1-05** de forma parcial: construir la **pantalla de Configuración de Tienda** consumiendo la API F1-03 ya construida por Nelson (commit `b83782a`, rama `feature/f1-03-config-nelson`), sin esperar los CRUDs de Productos/Proveedores (F1-01/F1-02, en curso o pendientes).

## 2. Alcance de este arranque parcial

| Elemento | Especificación |
|---|---|
| Pantalla | Configuración de Tienda (M-01): formulario de datos de la tienda |
| API consumida | `GET/PUT /api/v1/tienda/configuracion` — implementada en F1-03 |
| Patrón frontend | React 19 + Vite + TailwindCSS con tokens del design system (F0-05 ya consolidado) |
| Auth | Flujo JWT dual ya integrado (login/refresh/logout verificados en staging) |

> **Fuera de alcance de este arranque:** pantallas de Productos y Proveedores (esperan F1-01/F1-02 de Nelson) y UI de alertas (F1-06). Se delegarán por separado conforme el backend las entregue.

## 3. Instrucciones de ejecución

1. **Lectura previa:** `docs/INTEGRACION-BACKEND-FRONTEND.md` (contrato de integración vigente), patrón del scaffold F0-05 en `main`, y la API de F1-03 en el worktree de Nelson (`BodegApp-worktrees/f1-03-config-tienda`).
2. **Worktree asignado:** creá worktree `BodegApp-worktrees/f1-05-inventario` — rama `feature/f1-05-inventario-noris`. NO trabajes sobre `main`.
3. **Contrato:** consumí la API según la implementación real de F1-03 (endpoints GET/PUT `/api/v1/tienda/configuracion` con aislamiento tenant). Cualquier desalineación contrato↔implementación se reporta con formato obligatorio — no la "arregles" del lado frontend sin reportar.
4. **Estándar de calidad:** design system vigente (tokens Tailwind, tipografía, contraste WCAG AA), componentes reutilizables — esta pantalla sienta el patrón de las pantallas de inventario que siguen.
5. **Tests:** suite vitest conforme al patrón establecido (6/6 en remediación QA-F04-02/03 como referencia).
6. **Commit convencional** documentando autoría (autor: Noris, Frontend). NO pushear a main — merge requiere QA de Emilio.
7. **Reporte:** al terminar, reportás a Cristian con resumen + hallazgos con formato obligatorio.

## 4. Coordinación

- **Nelson (Backend):** construye F1-01 (CRUD Productos) en paralelo. Cuando la entregue, se te delega la siguiente pantalla del alcance F1-05.
- **Emilio (QA):** auditará tu pantalla al entregarse — no espera por él para arrancar la siguiente.
- **Staging:** el entorno online está disponible para pruebas manuales (ST-02 en curso por Emilio).

## 5. Fecha límite

**10/10/2026** para F1-05 completo (MATRIZ-ASIGNACION). Este arranque parcial (pantalla Tienda) debería entregarse **mucho antes** — es la primera pantalla de inventario y sienta el patrón. Bajo directiva de flujo continuo: al entregar, reportás y continuás con lo que el backend tenga disponible.

## 6. Protocolo de escalamiento

Bloqueo → marcar F1-05 🟠 en `docs/MATRIZ-ASIGNACION.md` con nota de quién traba + reporte inmediato a Cristian.

---

*Registrado en `docs/MATRIZ-ASIGNACION.md` (F1-05) — emitido por Cristian (Project Director), BodegApp 05/09/2026.*
