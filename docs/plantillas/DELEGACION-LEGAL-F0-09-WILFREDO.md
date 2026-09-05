# BodegApp — Delegación Formal: Validación Normativa del Ticket Fiscal (M-16)

> **Emisor:** Cristian (Project Director)
> **Fecha:** 05/09/2026
> **Destinatario:** Wilfredo (Legal/Compliance, Subsistema de Gobernanza Estratégica)
> **Referencia:** Entrega F0-09 de Nordanis (commit `d0ffff1`, rama `feature/f0-09-ticket-nordanis`) — hallazgos N-F009-04..08
> **Prioridad:** ALTA — la validación desbloquea el merge del diseño §10 y la implementación de M-16 en Fase 1+
> **Referencia de tarea:** LEG-01

---

## 1. Objetivo

Validar la **conformidad normativa venezolana** del diseño de Ticket Fiscal (§10 de `design/design-system.md`, entregado por Nordanis en F0-09) y resolver las 5 dudas legales que el diseño dejó como datos configurables.

## 2. Alcance — 5 puntos de validación

| Ref | Punto a validar | Detalle del diseño |
|---|---|---|
| N-F009-04 | **Naturaleza del comprobante** | ¿Es "no fiscal" tipo ticket de máquina fiscal (LEY DE IVA art. 70, Providencia SNAT/00003) o factura formal? Afecta nomenclatura "TICKET FISCAL" y campos: serial de máquina + identificación del cliente (bloque B del diseño) |
| N-F009-05 | **Leyenda de reimpresión** | Redacción exacta y número de reimpresiones admitidas (Providencia 00071/2014 art. 36 sugiere "REIMPRESIÓN" con especificaciones) |
| N-F009-06 | **Leyenda de anulación** | "No válido como comprobante fiscal" — ¿se requiere Nota de Crédito en lugar de ticket anulado? |
| N-F009-07 | **Alícuotas IVA** | 16%/8%/exentos aplicables y redacción exacta de "PRECIO CON IVA INCLUIDO" (Ley IVA art. 90, LGT art. 99) |
| N-F009-08 | **Formato del número de factura** | ¿`AAA-NN-NN-NNNNNN`? (Providencia 00071/2014) — el diseño usa `001-00012345` como placeholder |

## 3. Instrucciones de ejecución

1. **Lectura previa:** sección §10 de `design/design-system.md` en el worktree `/home/nedp/Desarrollo/Proyectos/BodegApp-worktrees/f0-09-ticket-fiscal` (rama `feature/f0-09-ticket-nordanis`, commit `d0ffff1`).
2. Validá cada punto contra la normativa fiscal VE vigente (leyes, providencias SNAT).
3. **Entregable:** dictamen legal por punto (conforme / requiere ajuste + redacción exacta cuando aplique), en un documento `docs/legal/DICTAMEN-TICKET-FISCAL.md` en tu worktree `BodegApp-worktrees/f4-03-compliance` (rama `feature/f4-03-compliance-wilfredo`, donde ya trabajás el marco preliminar F4-03) — o worktree nuevo si lo preferís.
4. Commit convencional: "docs(legal): LEG-01 dictamen normativo Ticket Fiscal M-16 — resuelve N-F009-04..08 (autor: Wilfredo, Legal)".
5. NO pushear a main — merge requiere autorización exclusiva de Cristian.

## 4. Reglas

- Todo hallazgo adicional con formato obligatorio (ref, descripción, severidad, acción, ¿bloquea producción?).
- Si un punto excede la normativa (requiere criterio del SENIAT o decisión de negocio), marcalo explícitamente como "requiere decisión del inversor" con las opciones y sus implicaciones.

## 5. Fecha límite

**12/09/2026** — habilita el QA de F0-09 (Emilio) con criterio legal completo y la implementación de M-16 en Fase 1+.

---

*Registrado en `docs/MATRIZ-ASIGNACION.md` (LEG-01) — emitido por Cristian (Project Director), BodegApp 05/09/2026.*
