# BodegApp — Directorio de Subagentes y Encargos

> Emitido por Cristian (Project Director) — 03/09/2026
> Cada subagente debe leer `docs/REQUERIMIENTOS.md` y `docs/MATRIZ-ASIGNACION.md` antes de iniciar su tarea.

## Célula de Desarrollo (Díaz Tech)

### Nordanis — UI/UX
**Encargo F0-01**: Analizar `design/referencias/modelo-referencia.png` (modelo de referencia del inversor) y construir el design system completo de BodegApp: tokens de color claro/oscuro según paleta definida en `docs/REQUERIMIENTOS.md` §4, tipografía (Plus Jakarta Sans para headlines, Inter para body), componentes base y prototipo en Penpot del flujo de inventario. Entregable en `design/`.

### Alfredo — DevOps
**Encargo F0-02**: docker-compose.yml endurecido bajo política Sentinel Shield v1.0: servicios API, Frontend, PostgreSQL, Zero Trust, gestión de secrets de Docker. Coordiná el diseño con Lead_Blue (F0-07) ANTES de implementar. Entregable en `infra/docker/`.

### Nelson — Backend
**Encargos F0-03/F0-04**: (1) Diseño del esquema PostgreSQL multi-tenant con propuesta de estrategia de aislamiento (schema-por-tenant vs RLS) — presentame la propuesta técnica para aprobación antes de implementar. (2) Autenticación JWT RS256 con tokens dual (contratante/trabajo). Entregables en `backend/`.

### Noris — Frontend
**Encargo F0-05**: Scaffold React 19 + Vite + TailwindCSS con routing protegido y arquitectura de tokens dual (contratante/trabajo). Consumí el design system de Nordanis (F0-01) apenas esté disponible. Entregable en `frontend/`.

### Carlos — Documentación
**Encargo F0-06**: Estructura de documentación: README raíz, guía de contribución, estándares de código por área, plantillas de documentación de APIs. Entregable en `docs/`.

### Emilio — QA
**Encargo F0-08**: Plan maestro de pruebas: matriz de pruebas por módulo (M-01..M-15), estrategia por fase, criterios de aceptación, definición de "done" por tarea. Entregable en `qa/` y `docs/qa/`.

### Javier — Java/JVM
**Encargo F1-08 (planificado)**: Motor de reportes JasperReports para el reporte de compras (M-07) en PDF, con arquitectura hexagonal y soporte cross-device. Inicia cuando Fase 1 esté en curso.

### Morloy — Data Science
**Encargo F1-07 (planificado)**: Diseño del reporte de compras (M-07): lógica de cálculo stock/mínimos, dashboard BI de alertas. Inicia en Fase 1.

### Victor — Go
**Encargos F3-02/F3-03 (planificados)**: Microservicio operational-stream (WebSocket, req 0-3) y parser de balanza digital USB/RJ45/RS-232 (M-15). Inicia en Fase 3.

### Alexis — Assembly
**Encargo F3-04 (planificado)**: Ingeniería inversa de protocolos de balanzas comerciales para alimentar el parser de Victor. Inicia en Fase 3.

### Sebastian — IA/MLOps
**Encargo F2-09 (planificado)**: Evaluación y arquitectura de integración WhatsApp Business API para el módulo de promociones (M-14). Inicia en Fase 2.

### Orlando — Marketing
**Encargo F2-08 (planificado)**: Estrategia de contenido y copy para plantillas de promociones WhatsApp (M-14). Inicia en Fase 2.

### Fernanda — Ofimática
**Encargo T-02 (transversal)**: Plantillas automatizadas para reportes al inversor (integración Notion/Drive vía MCP).

### Willian — AWS Cloud
**Encargo T-03 (transversal)**: Evaluación de infraestructura cloud para producción cuando el inversor lo requiera.

### Tosta — COBOL/Clipper
**Encargo T-04 (transversal)**: Consultoría de migración de datos legacy de bodegas existentes, si el inversor aporta sistemas previos.

## Célula de Ciberseguridad

### Lead_Blue — Blue Team (Sentinel Shield)
**Encargo F0-07**: Revisar y aprobar el diseño Zero Trust del docker-compose de Alfredo (F0-02) antes de su implementación. Luego: hardening continuo (F4-02), monitoreo (Monitor_Agent, T-05).

### Lead_Red — Red Team (Apollo Ultra)
**Encargo F4-01 (planificado)**: Pentest completo pre-lanzamiento: superficie de ataque, exploits simulados, IOC. Coordiná con Lead_Blue las reglas de enfrentamiento.

## Gobernanza Estratégica

### Ahides — Finanzas
**Encargo F4-04 (planificado)**: Modelo de costos del producto + proyección cash flow + estructura contable NIIF.

### Wilfredo — Legal/Compliance
**Encargo F4-03 (planificado)**: Matriz de cumplimiento: datos personales de deudores (fiados), clientes WhatsApp, GDPR/CCPA/PI, AML.

## Reglas para Todos los Subagentes

1. Leé `docs/REQUERIMIENTOS.md` (tu módulo) y `docs/MATRIZ-ASIGNACION.md` (tus tareas) antes de empezar.
2. Trabajá SIEMPRE en tu rama: `feature/<tu-area>-<ref-tarea>` (ej: `feature/backend-F0-03`).
3. NUNCA hagas push a `main`. El merge lo autoriza Cristian con QA + seguridad aprobados.
4. Reportá observaciones con el formato obligatorio (ref, descripción, severidad, acción, ¿bloquea producción?) — directiva del inversor: todo hallazgo se reporta, sin importar cuán mínimo parezca.
5. Si tu tarea se bloquea, marcá 🟠 en la MAT con nota de quién la traba.
