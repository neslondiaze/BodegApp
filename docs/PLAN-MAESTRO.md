# BodegApp — Plan Maestro de Proyecto

> Documento de gestión propiedad del Project Director (Cristian).
> Versión 1.0 — 03/09/2026

## 1. Visión

Sistema de inventario multi-tenant para bodegas del mercado venezolano, con fiados, tasa BCV automática, promociones WhatsApp e integración con balanzas digitales.

## 2. Arquitectura de Alto Nivel

```
┌─────────────────────────────────────────────────────────────┐
│                      BodegApp (Multi-Tenant)                 │
│                                                              │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────────┐ │
│  │   Frontend    │   │   Backend    │   │ operational-     │ │
│  │ React 19      │──▶│ FastAPI      │──▶│ stream (Go)      │ │
│  │ Vite          │   │ Python 3.12  │   │ WebSocket        │ │
│  │ TailwindCSS   │   │ JWT RS256    │   │ (Fase II)        │ │
│  └──────────────┘   └──────┬───────┘   └──────────────────┘ │
│                            │                                 │
│                     ┌──────┴───────┐                         │
│                     │ PostgreSQL   │  (tenant aislamiento)   │
│                     └──────────────┘                         │
│                                                              │
│  Integraciones: BCV scraping · WhatsApp · Balanza serial     │
│  Infra: docker-compose endurecido (Sentinel Shield v1.0)     │
└─────────────────────────────────────────────────────────────┘
```

## 3. Fases del Proyecto

### Fase 0 — Fundaciones (Semana 1-2)
- Monorepo, docker-compose base endurecido, CI básico
- Esquema multi-tenant PostgreSQL, JWT RS256 (tokens dual)
- Design system (paleta + tipografía definida por inversor)

### Fase 1 — Núcleo de Inventario (Semana 3-6)
- M-01 Configuración de tienda
- M-02 CRUD Productos
- M-03 CRUD Proveedores
- M-06 Alertas de mínimo
- M-07 Reporte de compras

### Fase 2 — Diferenciadores de Negocio (Semana 7-10)
- M-08/M-09 Fiados + historial
- M-10/M-11/M-12/M-13 BCV scraping + historial + scheduler
- M-14 Promociones WhatsApp

### Fase 3 — Hardware y Tiempo Real (Semana 11-14)
- M-04/M-05 Lector código barras / QR
- M-15 Integración balanza (USB/RJ45/RS-232)
- operational-stream (Go, WebSocket) — Fase II del stack

### Fase 4 — Endurecimiento y Lanzamiento (Semana 15-16)
- Pentest Red Team, hardening Blue Team final
- QA integral, UAT, despliegue a producción

## 4. Estrategia Multi-Tenant

- Aislamiento por tenant en PostgreSQL (estrategia a definir por Nelson con validación de Cristian: schema-por-tenant vs row-level security)
- Tokens dual (contratante/trabajo) definidos en requerimiento 0-2
- Zero Trust en docker-compose (requerimiento 0-4)

## 5. Gestión de Ramas Git

- `main` — propiedad exclusiva de Cristian. Prohibido push directo del equipo.
- Ramas por subagente: `feature/backend-*` (Nelson), `feature/frontend-*` (Noris), `feature/devops-*` (Alfredo), `feature/uiux-*` (Nordanis), `feature/go-*` (Victor), etc.
- Merge a main solo con: informe QA de Emilio ✅ + validación seguridad Lead_Blue/Lead_Red ✅ + autorización de Cristian
- Protocolo: `git checkout main` → `git merge [rama] --no-ff -m "Merge: Agente Líder integra [Tarea] de [Subagente]"` → `git push origin main`

## 6. Reportes al Inversor

- Vía MCP Notion (responsabilidad directa de Cristian)
- Cadencia: semanal (avance) y por hito (fin de fase)
- Contenido: estado de tareas, riesgos, presupuesto (Ahides), cumplimiento (Wilfredo)
