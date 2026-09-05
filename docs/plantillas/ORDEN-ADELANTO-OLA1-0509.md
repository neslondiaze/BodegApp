# BodegApp — Orden de Adelanto (Ola 1)

> **Emisor:** Cristian (Project Director)
> **Fecha:** 05/09/2026
> **Referencia:** Directiva del inversor — "adelanta todo lo posible" (máxima prioridad, flujo continuo)
> **Naturaleza:** activación anticipada de tareas con dependencias ya satisfechas o independientes del código
> **Documento:** `docs/plantillas/ORDEN-ADELANTO-OLA1-0509.md`

---

## 0. Verificación de fusionabilidad (gobernanza de merges)

✅ Verificado este 05/09: `feature/f0-02-bt-alfredo` (ST-01) y `feature/f1-03-config-nelson` (F1-03) **fusionan sin conflictos** contra `main`. Los merges quedan listos para ejecución inmediata apenas Emilio reporte los veredictos (ST-02 y auditoría F1-03 respectivamente).

## 1. Activaciones de la Fase 1 (camino crítico)

### 1.1 — F1-07 · Morloy (Data Science): Análisis del Reporte de Compras (M-07)

| Elemento | Especificación |
|---|---|
| Objetivo | Diseñar el análisis de stock/mínimos que alimenta el reporte de compras (M-07) y el dashboard asociado |
| Alcance | Modelo analítico: qué comprar, cuánto, cuándo (basado en stock actual vs mínimos, definidos en el esquema de F1-01); especificación de métricas y layout del dashboard |
| Entradas disponibles | `docs/REQUERIMIENTOS.md` (M-07), esquema multi-tenant de F0-03, diseño de tabla `productos` de F1-01 (en curso) |
| Entregable | Documento de especificación analítica + wireframe del dashboard, en worktree `BodegApp-worktrees/f1-07-reportes` — rama `feature/f1-07-reportes-morloy` |
| Fecha límite | 10/10/2026 (adelantada desde cola — arrancá HOY) |

### 1.2 — F1-08 · Javier (Java/JVM): Motor de Reportes JasperReports (M-07)

| Elemento | Especificación |
|---|---|
| Objetivo | Scaffolding del motor de reportes JasperReports que generará el reporte de compras en PDF |
| Alcance | Arquitectura Hexagonal del módulo de reportes: puertos/adaptadores, contrato de entrada de datos (lo consumirá la especificación de Morloy F1-07), esqueleto compilable con un reporte de prueba |
| Entradas disponibles | `docs/REQUERIMIENTOS.md` (M-07), arquitectura del proyecto en `docs/` |
| Entregable | Módulo compilable con tests, en worktree `BodegApp-worktrees/f1-08-jasper` — rama `feature/f1-08-jasper-javier` |
| Fecha límite | 14/10/2026 (adelantada desde cola — arrancá HOY) |
| Coordinación | Morloy (F1-07) define la especificación analítica en paralelo — el contrato de datos entre ambos se cierra en la revisión de ambos entregables |

### 1.3 — SR-01 · Lead_Blue (Blue Team): Revisión de Seguridad del Patrón Tenant (F1-03)

| Elemento | Especificación |
|---|---|
| Objetivo | Revisión de seguridad (solo lectura) del patrón de aislamiento multi-tenant implementado en F1-03 — es el patrón que Nelson replica en F1-01/F1-02/F1-04 |
| Alcance | Verificar el aislamiento tenant en `feature/f1-03-config-nelson` (commit `b83782a`): filtros por tenant en queries, autorización por token dual, imposibilidad de cross-tenant access |
| Entregable | Informe con formato obligatorio de observaciones (ref, ubicación, severidad, acción, ¿bloquea producción?) — **no bloquea el merge de F1-03** (gate de QA), pero condiciona el patrón de F1-01+ |
| Fecha límite | 08/09/2026 |
| Justificación | Si el patrón tiene una falla de aislamiento, debe detectarse ANTES de que Nelson construya 3 CRUDs encima |

## 2. Adelantos desde Fase 2 (trabajo independiente del código)

### 2.1 — F2-08 · Orlando (Marketing): Estrategia de Contenido Promocional (M-14)

| Elemento | Especificación |
|---|---|
| Objetivo | Estrategia de contenido promocional para WhatsApp + copy de las plantillas (M-14) |
| Alcance | Definición de tipos de campaña (ofertas, liquidación, reposición), tono de marca, calendario de envíos sugerido, y copy completo de 5 plantillas base |
| Entradas disponibles | `docs/REQUERIMIENTOS.md` (M-14) — NO requiere app construida |
| Entregable | Documento de estrategia + plantillas, en worktree `BodegApp-worktrees/f2-08-promos` — rama `feature/f2-08-promos-orlando` |
| Fecha límite | 07/11/2026 (adelantada — arrancá cuando Orlando tenga disponibilidad; prioridad media) |

### 2.2 — F2-09 · Sebastian (IA/MLOps): Evaluación WhatsApp Business API (M-14)

| Elemento | Especificación |
|---|---|
| Objetivo | Evaluación técnica de integración con WhatsApp Business API para envío de promociones (M-14) |
| Alcance | Proveedores (Meta Cloud API vs. agregadores), costos, límites de envío, proceso de aprobación de plantillas, requisitos de número verificado, arquitectura de integración recomendada (webhooks, opt-in/out) |
| Entradas disponibles | `docs/REQUERIMIENTOS.md` (M-14) — evaluación independiente |
| Entregable | Informe de evaluación con recomendación, en worktree `BodegApp-worktrees/f2-09-whatsapp` — rama `feature/f2-09-whatsapp-sebastian` |
| Fecha límite | 10/11/2026 (adelantada — arrancá HOY: la aprobación de plantillas/meta-verificación tiene lead time de semanas, adelantarla compra tiempo al proyecto) |

## 3. Adelantos desde Fase 4 (trabajo independiente)

### 3.1 — F4-04 · Ahides (Finanzas): Modelo de Costos + Cash Flow

| Elemento | Especificación |
|---|---|
| Objetivo | Modelo de costos del producto + proyección de cash flow (NIIF/IFRS/VEN-NIIF) |
| Alcance | Estructura de costos (infra, licencias, personal, WhatsApp API según evaluación F2-09), modelo de proyección, supuestos documentados |
| Entradas disponibles | Requerimientos completos, evaluación cloud de Willian (T-03, en paralelo) |
| Entregable | Modelo + informe, en worktree `BodegApp-worktrees/f4-04-finanzas` — rama `feature/f4-04-finanzas-ahides` |
| Fecha límite | 12/12/2026 (adelantada — arrancá cuando tengas disponibilidad; el inversor valora visibilidad financiera temprana) |

### 3.2 — F4-03 · Wilfredo (Legal/Compliance): Marco de Cumplimiento GDPR/CCPA/PI

| Elemento | Especificación |
|---|---|
| Objetivo | Marco preliminar de cumplimiento para datos de fiados (deudores) y clientes WhatsApp |
| Alcance | Matriz de cumplimiento: categorías de datos del sistema (ya conocidas por requerimientos), base legal, derechos del titular, retención; señalamiento de puntos que requieren decisión del inversor |
| Entradas disponibles | `docs/REQUERIMIENTOS.md` (M-08/M-09 fiados, M-14 WhatsApp) — las categorías de datos ya están definidas |
| Entregable | Matriz de cumplimiento preliminar, en worktree `BodegApp-worktrees/f4-03-compliance` — rama `feature/f4-03-compliance-wilfredo` |
| Fecha límite | 12/12/2026 (adelantada — el marco preliminar no depende del código) |

## 4. Activación de tareas continuas

### 4.1 — T-01 · Carlos (Documentación): Guía de Integración Fase 1

**Objetivo:** producir la guía de integración backend↔frontend para las APIs de Fase 1 (F1-03 ya construida, F1-01 en curso), consolidando el contrato real de `docs/INTEGRACION-BACKEND-FRONTEND.md` con evidencia de las implementaciones. **Contexto:** las desalineaciones contrato↔implementación (QA-F04-07/08) costaron remediación — esta guía las previene para Noris (F1-05). Worktree `BodegApp-worktrees/t01-guias` — rama `feature/t01-guias-carlos`. **Entregable parcial esperado: 12/09/2026** (guía de la API Tienda F1-03).

### 4.2 — T-02 · Fernanda (Ofimática): Plantillas de Reportes al Inversor

**Objetivo:** familia de plantillas para los reportes al inversor (formato RI-001 como base) con automatización para publicación Notion/Drive. **Entregable:** 3 plantillas (avance quincenal, hitos/fases, estado financiero) + instructivo de uso. Worktree `BodegApp-worktrees/t02-plantillas` — rama `feature/t02-plantillas-fernanda`. **Entregable parcial esperado: 12/09/2026.**

### 4.3 — T-03 · Willian (AWS Cloud): Evaluación de Infraestructura Cloud

**Objetivo:** evaluación de infraestructura cloud para producción (si el inversor requiere salida a cloud en diciembre): opciones (AWS ECS/Lightsail vs. VPS), costos comparados con el host actual, alta disponibilidad, plan de migración. **Entregable:** informe de evaluación con recomendación. Worktree `BodegApp-worktrees/t03-cloud` — rama `feature/t03-cloud-willian`. **Fecha límite: 26/09/2026** (alimenta la decisión de producción y el modelo de costos de Ahides F4-04).

## 5. Reglas comunes a todas las activaciones

1. **Todo hallazgo se reporta** con el formato obligatorio (ref, descripción con ubicación, severidad, acción correctiva, ¿bloquea producción?) — directiva del inversor.
2. **NO se trabaja sobre `main`** — cada recurso en su worktree/rama; merges exclusivos vía Cristian con QA aprobado.
3. **Commits convencionales** documentando autoría.
4. **Flujo continuo:** al entregar, se reporta y se arranca la siguiente tarea disponible — sin tiempos muertos.
5. **Escalada:** bloqueo → marcar 🟠 en `docs/MATRIZ-ASIGNACION.md` con nota de quién traba + reporte inmediato a Cristian.

## 6. Cola de pipeline aclarada (sin delegación nueva — ya asignadas)

| Tarea | Recurso | Condición de arranque |
|---|---|---|
| F1-02 (CRUD Proveedores) | Nelson | Al entregar F1-01 |
| F1-04 (Motor de alertas M-06) | Nelson | Al entregar F1-02 |
| F1-09 (Suite QA Fase 1) | Emilio | Al liberarse de ST-02 + auditoría F1-03 |
| Auditoría QA F1-03 | Emilio | Inmediatamente tras ST-02 (o en paralelo si el smoke test lo permite) |

---

*Registrado en `docs/MATRIZ-ASIGNACION.md` — emitido por Cristian (Project Director), BodegApp 05/09/2026.*
