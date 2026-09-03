# BodegApp — Matriz de Asignación de Tareas (MAT)

> Documento vivo. Actualizado por Cristian (Project Director).
> Estados: 🔴 Pendiente | 🟡 En Progreso | 🔵 En Revisión | 🟢 Completado | 🟠 Bloqueado

## Fase 0 — Fundaciones

| Ref | Recurso / Célula | Rol | Tarea Asignada | Estado | Fecha Límite |
|-----|------------------|-----|----------------|--------|--------------|
| F0-01 | Nordanis | UI/UX | Analizar imagen `design/referencias/modelo-referencia.png` y producir design system (paleta claro/oscuro + tipografía Plus Jakarta Sans/Inter) en tokens Tailwind | 🔴 | 08/09/2026 |
| F0-02 | Alfredo | DevOps | docker-compose.yml endurecido (Sentinel Shield v1.0): API, Frontend, PostgreSQL, Zero Trust, secrets Docker | 🔴 | 10/09/2026 |
| F0-03 | Nelson | Backend | Esquema PostgreSQL multi-tenant + estrategia de aislamiento (propuesta técnica a Cristian) | 🔴 | 12/09/2026 |
| F0-04 | Nelson | Backend | Autenticación JWT RS256 con tokens dual (contratante/trabajo) | 🔴 | 15/09/2026 |
| F0-05 | Noris | Frontend | Scaffold React 19 + Vite + TailwindCSS con routing protegido y arquitectura de tokens dual | 🔴 | 15/09/2026 |
| F0-06 | Carlos | Documentación | Estructura de documentación del proyecto (README, guías de contribución, estándares) | 🔴 | 12/09/2026 |
| F0-07 | Lead_Blue | Blue Team | Revisar y aprobar diseño Zero Trust de F0-02 antes de implementación | 🔴 | 09/09/2026 |
| F0-08 | Emilio | QA | Plan maestro de pruebas + estrategia de testing por fase | 🔴 | 15/09/2026 |

## Fase 1 — Núcleo de Inventario

| Ref | Recurso / Célula | Rol | Tarea Asignada | Estado | Fecha Límite |
|-----|------------------|-----|----------------|--------|--------------|
| F1-01 | Nelson | Backend | API CRUD Productos (M-02) con aislamiento tenant | 🔴 | 26/09/2026 |
| F1-02 | Nelson | Backend | API CRUD Proveedores (M-03) | 🔴 | 30/09/2026 |
| F1-03 | Nelson | Backend | API Configuración de Tienda (M-01) | 🔴 | 24/09/2026 |
| F1-04 | Nelson | Backend | Motor de alertas de mínimo de stock (M-06) | 🔴 | 03/10/2026 |
| F1-05 | Noris | Frontend | Pantallas CRUD Productos/Proveedores/Tienda consumiendo APIs F1-01..03 | 🔴 | 10/10/2026 |
| F1-06 | Noris | Frontend | UI de alertas de mínimo (M-06) | 🔴 | 14/10/2026 |
| F1-07 | Morloy | Data Science | Reporte de compras (M-07): análisis de stock/mínimos, diseño de dashboard | 🔴 | 10/10/2026 |
| F1-08 | Javier | Java/JVM | Motor de reportes JasperReports para reporte de compras PDF (M-07) | 🔴 | 14/10/2026 |
| F1-09 | Emilio | QA | Suite de pruebas Fase 1 (CRUDs, alertas, multi-tenant) | 🔴 | 17/10/2026 |

## Fase 2 — Diferenciadores de Negocio

| Ref | Recurso / Célula | Rol | Tarea Asignada | Estado | Fecha Límite |
|-----|------------------|-----|----------------|--------|--------------|
| F2-01 | Nelson | Backend | API Fiados (M-08): abono a cuenta + fecha de pago | 🔴 | 24/10/2026 |
| F2-02 | Nelson | Backend | API Historial de fiados (M-09) | 🔴 | 28/10/2026 |
| F2-03 | Nelson | Backend | Scraping BCV (M-10) + actualización dólar (M-11) | 🔴 | 31/10/2026 |
| F2-04 | Nelson | Backend | Scheduler de scraping configurable por días/horas (M-13) | 🔴 | 04/11/2026 |
| F2-05 | Noris | Frontend | Pantallas Fiados + Historial + Tipo de cambio (M-08/09/12) | 🔴 | 07/11/2026 |
| F2-06 | Noris | Frontend | UI configuración de scraping (M-13) | 🔴 | 10/11/2026 |
| F2-07 | Nordanis | UI/UX | Diseño de plantillas de promociones WhatsApp (M-14) | 🔴 | 07/11/2026 |
| F2-08 | Orlando | Marketing | Estrategia de contenido promocional + copy de plantillas (M-14) | 🔴 | 07/11/2026 |
| F2-09 | Sebastian | IA/MLOps | Evaluación de integración WhatsApp Business API para envío de promociones (M-14) | 🔴 | 10/11/2026 |
| F2-10 | Emilio | QA | Suite de pruebas Fase 2 (fiados, scraping, promociones) | 🔴 | 14/11/2026 |

## Fase 3 — Hardware y Tiempo Real

| Ref | Recurso / Célula | Rol | Tarea Asignada | Estado | Fecha Límite |
|-----|------------------|-----|----------------|--------|--------------|
| F3-01 | Noris | Frontend | Lector código de barras (M-04) y QR (M-05) en frontend | 🔴 | 21/11/2026 |
| F3-02 | Victor | Go | Microservicio operational-stream: ingesta WebSocket (req 0-3) | 🔴 | 28/11/2026 |
| F3-03 | Victor | Go | Parser para balanza digital: USB, RJ45, RS-232 (M-15) | 🔴 | 05/12/2026 |
| F3-04 | Alexis | Assembly | Ingeniería inversa de protocolos de balanzas comerciales (soporte a Victor) | 🔴 | 28/11/2026 |
| F3-05 | Alfredo | DevOps | Despliegue operational-stream en compose + networking seguro | 🔴 | 05/12/2026 |
| F3-06 | Emilio | QA | Suite de pruebas Fase 3 (lectores, balanza, WebSocket) | 🔴 | 12/12/2026 |

## Fase 4 — Endurecimiento y Lanzamiento

| Ref | Recurso / Célula | Rol | Tarea Asignada | Estado | Fecha Límite |
|-----|------------------|-----|----------------|--------|--------------|
| F4-01 | Lead_Red | Red Team | Pentest completo pre-lanzamiento (Apollo Ultra) | 🔴 | 19/12/2026 |
| F4-02 | Lead_Blue | Blue Team | Hardening final + validación Sentinel Shield | 🔴 | 19/12/2026 |
| F4-03 | Wilfredo | Legal/Compliance | Revisión GDPR/CCPA/PI: datos de fiados (deudores) y clientes WhatsApp | 🔴 | 12/12/2026 |
| F4-04 | Ahides | Finanzas | Modelo de costos + proyección cash flow del producto | 🔴 | 12/12/2026 |
| F4-05 | Emilio | QA | UAT integral + informe de calidad final | 🔴 | 22/12/2026 |
| F4-06 | Alfredo | DevOps | Despliegue a producción + plan de rollback | 🔴 | 24/12/2026 |

## Soporte Transversal (Continuo)

| Ref | Recurso | Rol | Tarea Asignada | Estado | Fecha Límite |
|-----|---------|-----|----------------|--------|--------------|
| T-01 | Carlos | Documentación | Guías de integración backend↔frontend, estándares de código | 🔴 | Continuo |
| T-02 | Fernanda | Ofimática | Plantillas de reportes al inversor (automatización Notion/Drive) | 🔴 | Continuo |
| T-03 | Willian | AWS Cloud | Evaluación de infraestructura cloud para producción (si el inversor requiere) | 🔴 | Continuo |
| T-04 | Tosta | COBOL/Clipper | Consultoría de migración de datos legacy de bodegas (si aplica) | 🔴 | Continuo |
| T-05 | Monitor_Agent (Blue) | Vigilancia | Monitoreo continuo de logs/telemetría desde primer despliegue | 🔴 | Continuo |

## Dependencias Críticas

- **F0-02 → F0-03/F0-05**: Nelson y Noris dependen del entorno Docker de Alfredo.
- **F0-03/F0-04 → F1-01..04**: las APIs de Fase 1 requieren esquema y auth terminados.
- **F1-01..03 → F1-05**: Noris requiere las APIs de Nelson para integrar.
- **F3-03 → F3-04**: el parser de balanza requiere el análisis de protocolos de Alexis.
- **F4-01/F4-02 → F4-06**: el despliegue a producción requiere pentest y hardening aprobados.
