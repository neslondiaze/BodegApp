# BodegApp — Matriz de Asignación de Tareas (MAT)

> Documento vivo. Actualizado por Cristian (Project Director).
> Estados: 🔴 Pendiente | 🟡 En Progreso | 🔵 En Revisión | 🟢 Completado | 🟠 Bloqueado

## Fase 0 — Fundaciones

| Ref | Recurso / Célula | Rol | Tarea Asignada | Estado | Fecha Límite |
|-----|------------------|-----|----------------|--------|--------------|
| F0-01 | Nordanis | UI/UX | Analizar imagen `design/referencias/modelo-referencia.png` y producir design system (paleta claro/oscuro + tipografía Plus Jakarta Sans/Inter) en tokens Tailwind | 🔵 En Revisión | 08/09/2026 |
| F0-02 | Alfredo | DevOps | docker-compose.yml endurecido (Sentinel Shield v1.0): API, Frontend, PostgreSQL, Zero Trust, secrets Docker | 🔵 En Revisión | 10/09/2026 |
| F0-03 | Nelson | Backend | Esquema PostgreSQL multi-tenant + estrategia de aislamiento (propuesta técnica a Cristian) | 🟢 Completado | 12/09/2026 |
| F0-04 | Nelson | Backend | Autenticación JWT RS256 con tokens dual (contratante/trabajo) | 🟢 Completado | 15/09/2026 |
| F0-05 | Noris | Frontend | Scaffold React 19 + Vite + TailwindCSS con routing protegido y arquitectura de tokens dual | 🔵 En Revisión | 15/09/2026 |
| F0-06 | Carlos | Documentación | Estructura de documentación del proyecto (README, guías de contribución, estándares) | 🔵 En Revisión | 12/09/2026 |
| F0-07 | Lead_Blue | Blue Team | Revisar y aprobar diseño Zero Trust de F0-02 antes de implementación | 🟢 Completado | 09/09/2026 |
| F0-08 | Emilio | QA | Plan maestro de pruebas + estrategia de testing por fase | 🔵 En Revisión | 15/09/2026 |
| F0-09 | Nordanis | UI/UX | Diseño de Ticket Fiscal (M-16) en design-system.md §10: formatos 58/80mm, campos fiscales VE, reimpresión marcada y anulación | 🟡 En Progreso | 10/09/2026 |

> **Notas de consolidación (04/09/2026, Cristian):** Fase 0 consolidada a `main` vía merges `--no-ff` por célula (7 fusiones) tras autorización del inversor. F0-03 y F0-04 completados y auditados por QA (42/42 tests, 97% cobertura). F0-07 gate cerrado: Lead_Blue aprobó F0-02 con 6 observaciones no bloqueantes (BT-01..BT-06, registro abajo). Deuda F0-01: 10 ítems abiertos (OBS-06, OBS-09 del lote 1; OBS-07, OBS-08, OBS-10, OBS-11, OBS-12, O-N-003, O-N-004, R-03 del lote 2) — OBS-04 y OBS-05 remediados y verificados por QA esta sesión. O-N-005 resuelto 04/09/2026 (noche): el inversor autorizó soportar Ticket Fiscal como M-16 — diseño delegado a Nordanis (F0-09).

> **Registro de observaciones Blue Team — gate F0-07/F0-02 (Lead_Blue, 04/09/2026):** Veredicto ⚠️ APROBADO CON OBSERVACIONES. Ninguna bloquea producción.

| Ref | Descripción | Severidad | Acción correctiva | Responsable | Estado |
|-----|-------------|-----------|-------------------|-------------|--------|
| BT-01 | Sin `.dockerignore` en frontend/ y backend/; `COPY . .` arrastra node_modules al build | Media | Crear .dockerignore en ambos contextos | Alfredo | 🟡 |
| BT-02 | `secrets/postgres_password.txt` con modo 0644 en host (resto 0600) | Media | chmod 0600 + documentar provisión | Alfredo | 🟡 |
| BT-03 | `/tmp` del api sin noexec pese a staging de claves en /tmp/keys | Media | Separar staging a /run/keys noexec | Alfredo | 🟡 |
| BT-04 | uvicorn `--forwarded-allow-ips '*'` confía en cualquier peer (mitigado por segmentación) | Media | Restringir a IP del proxy | Alfredo | 🟡 |
| BT-05 | CSP con `style-src 'unsafe-inline'` | Baja | Migrar a nonce (fase posterior) | Alfredo | 🟡 |
| BT-06 | Masters arrancan como root antes del drop (patrón documentado) | Baja | Verificar runtime en F0-08 | Alfredo + Emilio | 🟡 |

> Condición de Lead_Blue: BT-01 y BT-02 deben resolverse **antes del deploy a producción**. BT-04 sugerido al backlog de hardening F1.

> **Delegaciones 04/09/2026 (noche, Cristian — autorizadas por el inversor):** F0-09 diseño M-16 §10 (Nordanis), remediación BT-01..BT-06 (Alfredo), arranque F1-03 (Nelson). Cada subagente trabaja en worktree propio sobre su rama feature; el merge a main requiere QA de Emilio aprobado.

> **Recordatorios formales de arranque 05/09/2026 (Cristian):** Emitidos a Alfredo (BT-01..06, worktree sin actividad) y Nordanis (F0-09, worktree sin actividad) — verificados worktrees limpios sin commits. Documentos: `docs/plantillas/RECORDATORIO-ARRANQUE-ALFREDO.md` y `docs/plantillas/RECORDATORIO-ARRANQUE-NORDANIS.md`. Ambos con fecha límite 10/09/2026.

> **Staging online autorizado 05/09/2026 (Cristian — autorización del inversor, Opción A):** ST-01 deploy staging restringido (Alfredo, incluye BT-01/BT-02, vence 08/09) + ST-02 smoke test post-deploy (Emilio, 09/09). NO es producción: TLS dev, datos de prueba. La ruta a producción formal sigue siendo F4-06 con gates F4-01/F4-02. Documento: `docs/plantillas/DELEGACION-ST01-STAGING-ALFREDO.md`.

## Fase 1 — Núcleo de Inventario

| Ref | Recurso / Célula | Rol | Tarea Asignada | Estado | Fecha Límite |
|-----|------------------|-----|----------------|--------|--------------|
| F1-01 | Nelson | Backend | API CRUD Productos (M-02) con aislamiento tenant | 🔴 | 26/09/2026 |
| F1-02 | Nelson | Backend | API CRUD Proveedores (M-03) | 🔴 | 30/09/2026 |
| F1-03 | Nelson | Backend | API Configuración de Tienda (M-01) | 🟡 En Progreso | 24/09/2026 |
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

## Staging Online (Autorizado por el inversor — 05/09/2026)

| Ref | Recurso | Rol | Tarea Asignada | Estado | Fecha Límite |
|-----|---------|-----|----------------|--------|--------------|
| ST-01 | Alfredo | DevOps | Deploy staging online restringido: stack completo, TLS dev, BT-01/BT-02 incluidos, datos de prueba | 🟡 En Progreso | 08/09/2026 |
| ST-02 | Emilio | QA | Smoke test post-deploy sobre staging online (login/refresh/logout/dashboard) | 🔴 Pendiente (tras ST-01) | 09/09/2026 |

## Dependencias Críticas

- **F0-02 → F0-03/F0-05**: Nelson y Noris dependen del entorno Docker de Alfredo.
- **F0-03/F0-04 → F1-01..04**: las APIs de Fase 1 requieren esquema y auth terminados.
- **F1-01..03 → F1-05**: Noris requiere las APIs de Nelson para integrar.
- **F3-03 → F3-04**: el parser de balanza requiere el análisis de protocolos de Alexis.
- **F4-01/F4-02 → F4-06**: el despliegue a producción requiere pentest y hardening aprobados.
