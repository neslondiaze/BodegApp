# BodegApp — Delegación Formal: API CRUD Productos (M-02)

> **Emisor:** Cristian (Project Director)
> **Fecha:** 05/09/2026
> **Destinatario:** Nelson (Backend, Célula Díaz Tech)
> **Referencia:** Directiva del inversor — flujo continuo entre fases (máxima prioridad)
> **Prioridad:** 🔴 ALTA — F1-03 entregada; arrancás la siguiente fase sin esperar QA
> **Referencia de tarea:** F1-01

---

## 1. Objetivo

Construir la **API CRUD Productos (M-02)** con aislamiento multi-tenant, siguiendo el patrón arquitectónico ya establecido en F1-03 (API Configuración de Tienda). Bajo la directiva de flujo continuo del inversor, **no esperás el veredicto QA de F1-03** — Emilio la auditará en paralelo.

## 2. Alcance funcional (M-02)

| Elemento | Especificación |
|---|---|
| Operaciones | Alta / baja / modificación / consulta de productos |
| Aislamiento | Multi-tenant estricto — un producto pertenece a una tienda; sin cross-tenant leaks |
| Campos base | Nombre, código/sku, precio, stock actual, stock mínimo, proveedor (relación M-03), unidad de medida |
| Validaciones | Unicidad de código por tienda, stock no negativo, precios decimales |
| Contrato | REST `/api/v1/productos` — alineado al contrato de `docs/INTEGRACION-BACKEND-FRONTEND.md` (§ productos) |

> **Nota de dependencia:** la relación con proveedores (M-03) se define ahora a nivel de esquema (FK), pero el CRUD de proveedores completo es F1-02 (30/09). No construyas endpoints de proveedores en esta tarea.

## 3. Instrucciones de ejecución

1. **Lectura previa:** `docs/REQUERIMIENTOS.md` (M-02), `docs/INTEGRACION-BACKEND-FRONTEND.md` (contrato productos), patrón de F1-03 en tu worktree (`feature/f1-03-config-nelson`, commit `b83782a`).
2. **Worktree asignado:** creá worktree `BodegApp-worktrees/f1-01-productos` — rama `feature/f1-01-productos-nelson`. NO trabajes sobre `main`.
3. **Esquema:** migración alembic para tabla `productos` con FK a tenant + FK a proveedor (nullable hasta F1-02).
4. **Tests:** suite completa con aislamiento tenant verificado (patrón de los 24 tests de F1-03) — un tenant no puede ver/modificar productos de otro.
5. **Commit convencional** documentando autoría (autor: Nelson, Backend). NO pushear a main — merge requiere QA de Emilio.
6. **Reporte:** al terminar, reportás a Cristian con resumen + hallazgos con formato obligatorio (ref, descripción, severidad, acción, ¿bloquea producción?).

## 4. Coordinación

- **Emilio (QA):** audita F1-03 en paralelo — no te retiene. Tu F1-01 se auditará al entregarse.
- **Noris (Frontend):** arranca en paralelo la pantalla de Configuración de Tienda (F1-05 parcial) sobre la API F1-03 ya construida. Tu CRUD Productos alimentará sus pantallas de inventario después.
- **Alfredo (DevOps):** el staging corre la API con migraciones automáticas al arranque — coordinaré con él el redeploy cuando F1-01 esté lista para staging.

## 5. Fecha límite

**26/09/2026** (MATRIZ-ASIGNACION F1-01). Bajo directiva de flujo continuo: si terminás antes, reportás y arrancás F1-02 (CRUD Proveedores) de inmediato.

## 6. Protocolo de escalamiento

Bloqueo → marcar F1-01 🟠 en `docs/MATRIZ-ASIGNACION.md` con nota de quién traba + reporte inmediato a Cristian.

---

*Registrado en `docs/MATRIZ-ASIGNACION.md` (F1-01) — emitido por Cristian (Project Director), BodegApp 05/09/2026.*
