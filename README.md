# BodegApp

Sistema de inventario multi-tenant para bodegas del mercado venezolano.

## Stack

- **Backend**: FastAPI (Python 3.12) + PostgreSQL + JWT RS256 (tokens dual)
- **Frontend**: React 19 + Vite + TailwindCSS
- **Tiempo real**: operational-stream (Go, WebSocket) — Fase II
- **Infra**: docker-compose endurecido (Sentinel Shield v1.0)

## Estructura del Repositorio

```
backend/            # API FastAPI (Nelson)
frontend/           # App React (Noris)
operational-stream/ # Microservicio Go (Victor)
infra/              # Docker / despliegue (Alfredo)
design/             # Design system y referencias (Nordanis)
qa/                 # Planes e informes de QA (Emilio)
security/           # Blue Team / Red Team
data/               # Datos y migraciones
docs/               # Gestión del proyecto (Cristian)
```

## Documentación de Gestión

- [Requerimientos](docs/REQUERIMIENTOS.md) — fuente de verdad funcional
- [Plan Maestro](docs/PLAN-MAESTRO.md) — fases, arquitectura, git
- [Matriz de Asignación](docs/MATRIZ-ASIGNACION.md) — tareas por subagente

## Gestión de Ramas

`main` es propiedad exclusiva del Project Director (Cristian). Todo trabajo se realiza en ramas `feature/<area>-<tarea>` y se fusiona con `--no-ff` previa aprobación de QA y seguridad.
