# Reporte al Inversor — Staging Online BodegApp

> **Reporte:** RI-001 · **Fecha:** 05/09/2026
> **Emisor:** Cristian (Project Director)
> **Destinatario:** Inversor
> **Estado del staging:** 🟡 Deploy en curso (ST-01) — acceso a entregar tras control de calidad (ST-02)

---

## Resumen ejecutivo

Conforme a su autorización del 05/09/2026 (Opción A), el equipo está desplegando un entorno **staging online** de BodegApp para que pueda verificar el avance tangible del sistema. El despliegue está a cargo de Alfredo (DevOps) con fecha límite **08/09/2026**, sujeto a control de calidad de Emilio (QA) antes de entregarle el acceso.

## Estado del proyecto al 05/09/2026

| Área | Avance | Evidencia |
|------|--------|-----------|
| **Fase 0 — Fundaciones** | Consolidada en rama principal (7 fusiones auditadas) | Esquema multi-tenant, infraestructura Docker Zero Trust, design system, documentación |
| **Autenticación (F0-04)** | 🟢 Completado y auditado | 42/42 pruebas aprobadas, 97% cobertura — JWT RS256 con tokens dual (contratante/trabajo) |
| **Gate de seguridad (F0-07)** | 🟢 Cerrado | Blue Team aprobó el diseño Zero Trust con 6 observaciones en remediación |
| **Fase 1 — Núcleo de Inventario** | 🟡 En desarrollo | API de Configuración de Tienda en curso (Nelson); CRUD Productos/Proveedores y alertas programados para septiembre-octubre |
| **Ticket Fiscal (M-16)** | 🟡 Diseño en curso | Su decisión del 04/09 registrada; diseño delegado a Nordanis (vence 10/09) |

## Qué verá en el staging

El staging muestra el **estado real del producto hoy**: autenticación completa (login, renovación de sesión, cierre con revocación) y el dashboard base. Las pantallas de inventario (productos, proveedores, alertas de stock) se incorporarán conforme avance la Fase 1 (septiembre-octubre).

> **Importante:** el staging NO es producción. Usa certificados de desarrollo y datos de prueba. La puesta en producción formal está planificada para diciembre, precedida por pentest del Red Team y hardening final del Blue Team (F4-01/F4-02).

## Cronograma próximo

| Hito | Responsable | Fecha |
|------|-------------|-------|
| Deploy staging operativo | Alfredo (DevOps) | **HOY 05/09/2026 (inmediato, por su directiva)** |
| Smoke test de calidad | Emilio (QA) | Inmediatamente tras el deploy |
| **Entrega de acceso al inversor** | Cristian (Project Director) | **Hoy, tras el smoke test** |
| Diseño Ticket Fiscal (M-16) | Nordanis (UI/UX) | 10/09/2026 |
| APIs Fase 1 (CRUDs + alertas) | Nelson (Backend) | 24/09 – 03/10/2026 |

## Acceso al staging

> 🔒 **Pendiente de provisión** — se entregará junto con la confirmación del smoke test (ST-02). El acceso es restringido y de uso exclusivo del inversor.

---

*Preparado por Cristian (Project Director) — BodegApp, 05/09/2026. Canal de entrega: informe directo + publicación en Notion/Drive (T-02).*
