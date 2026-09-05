# BodegApp — Recordatorio Formal de Arranque

> **Emisor:** Cristian (Project Director)
> **Fecha:** 05/09/2026
> **Destinatario:** Nordanis (UI/UX, Célula Díaz Tech)
> **Referencia:** Delegación 04/09/2026 (noche) — autorizada por el inversor
> **Prioridad:** ALTA — resuelve la decisión M-16 del inversor (Ticket Fiscal)

---

## 1. Motivo del recordatorio

La delegación formal del diseño de Ticket Fiscal (F0-09, M-16 §10) fue emitida la noche del 04/09/2026. A la fecha, tu worktree asignado (`BodegApp-worktrees/f0-09-ticket-fiscal`, rama `feature/f0-09-ticket-nordanis`) **no registra commits ni archivos modificados**. Este documento constituye el recordatorio formal de arranque.

## 2. Alcance de la tarea

**F0-09 — Diseño de Ticket Fiscal (M-16)** como nueva sección §10 de `design/design-system.md`:

| Elemento | Especificación |
|----------|----------------|
| Formatos | 58mm y 80mm |
| Campos fiscales | Según normativa VE (razón social, RIF, número de factura, fecha/hora, base imponible, IVA, total) |
| Reimpresión | Marcada visualmente como REIMPRESIÓN |
| Anulación | Tratamiento visual de ticket anulado |
| Tipografía | Monoespaciada para impresión térmica (consistente con el design system vigente) |

> Contexto: M-16 fue agregado a `docs/REQUERIMIENTOS.md` (línea 39) por decisión del inversor del 04/09/2026, resolviendo la observación O-N-005. El design system actual llega hasta §9 — tu sección es la §10.

## 3. Instrucciones de ejecución

1. **Lectura previa obligatoria:** `docs/REQUERIMIENTOS.md` (M-16, línea 39), `design/design-system.md` completo (§1..§9 — especialmente §2 tipografía, §5 componentes, §7 accesibilidad y contraste WCAG AA), y `docs/MATRIZ-ASIGNACION.md` (F0-09).
2. **Worktree asignado:** `BodegApp-worktrees/f0-09-ticket-fiscal` — rama `feature/f0-09-ticket-nordanis`. Todo tu trabajo se realiza ahí; NO trabajes sobre `main`.
3. **Alcance de archivos:** exclusivamente `design/design-system.md` (nueva §10). Si necesitás assets adicionales (mockups del ticket), van en `design/` dentro de tu worktree.
4. **Estándar de calidad:** mantené la estructura documental del design system (tablas de tokens, evidencia de contraste §7, gobernanza §8). El ticket fiscal es un documento legal-fiscal: priorizá legibilidad y cumplimiento de campos obligatorios VE sobre estética.
5. **Reporte de observaciones:** cualquier hallazgo (inconsistencias en el design system, dudas sobre campos fiscales VE) se reporta con el formato obligatorio (ref, descripción con ubicación exacta, severidad, acción correctiva, ¿bloquea producción?) — directiva del inversor: todo hallazgo se reporta, sin importar cuán mínimo parezca.
6. **Cierre:** al terminar, reportá a Cristian para derivar a QA (Emilio). El merge a `main` requiere QA aprobado — autorización exclusiva de Cristian.

## 4. Fecha límite

**10/09/2026** (según MATRIZ-ASIGNACION, F0-09 🟡 En Progreso). Este diseño desbloquea la implementación del ticket fiscal en Fase 1+ (Nelson/Noris lo consumirán para API e impresión).

## 5. Protocolo de escalamiento

Si encontrás algún bloqueo (dudas sobre normativa fiscal VE que requieran validación de Wilfredo, dependencia del design system), marcá la tarea 🟠 en `docs/MATRIZ-ASIGNACION.md` con nota de quién la traba y reportá inmediatamente a Cristian. No esperes a la fecha límite para escalar.

---

*Registro de este recordatorio en `docs/MATRIZ-ASIGNACION.md` — emitido por Cristian (Project Director), BodegApp 05/09/2026.*
