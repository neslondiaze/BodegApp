# BodegApp — Estándares de Código por Área

> Norma técnica obligatoria para todos los subagentes de desarrollo. Cada área define estructura de carpetas, naming, manejo de errores y tests mínimos exigidos. La verificación de estos estándares es criterio de QA (Emilio) previo a todo merge.

## Cómo usar este documento

1. Ubicá tu área en la tabla de abajo.
2. Seguí sus reglas de estructura y naming antes de escribir la primera línea.
3. Verificá el checklist final antes de solicitar merge (ver `CONTRIBUTING.md`).

## Mapa de responsabilidades

| Área | Responsable | Raíz |
|------|-------------|------|
| Python / FastAPI (Backend) | Nelson | `backend/` |
| TypeScript / React (Frontend) | Noris | `frontend/` |
| Go (operational-stream) | Victor | `operational-stream/` |
| Docker / Infraestructura | Alfredo | `infra/` |

---

## 1. Python / FastAPI — Backend (Nelson)

### Estructura de carpetas

```
backend/
├── src/
│   ├── main.py              # Punto de entrada, fábrica de la app
│   ├── core/                # Config, seguridad, dependencias transversales
│   │   ├── config.py
│   │   └── security.py      # JWT RS256, tokens dual
│   ├── api/v1/              # Routers por recurso, versionado /api/v1
│   │   └── <recurso>.py
│   ├── models/              # Modelos SQLAlchemy (ORM)
│   ├── schemas/              # Esquemas Pydantic (request/response)
│   ├── services/             # Lógica de negocio
│   ├── repositories/         # Acceso a datos, aislamiento tenant
│   ├── └── tests/            # Tests pytest
```

### Naming

| Elemento | Convención | Ejemplo |
|----------|------------|---------|
| Módulos | `snake_case` | `producto_service.py` |
| Clases | `PascalCase` | `ProductoService` |
| Funciones/métodos | `snake_case`, verbos | `crear_producto()` |
| Constantes | `SNAKE_CASE` superior | `TASA_MAX_BCV` |
| Modelos ORM | Singular, PascalCase | `Producto`, `Fiado` |
| Endpoints | Plural kebab/camel según URL | `/api/v1/productos` |
| Variables de entorno | Prefijo `BODEGAPP_` | `BODEGAPP_DATABASE_URL` |

### Manejo de errores

| Regla | Detalle |
|-------|---------|
| Formato de error | JSON uniforme según contrato de `docs/INTEGRACION-BACKEND-FRONTEND.md` |
| Excepciones de dominio | Definir en `src/core/exceptions.py`; nunca propagar `Exception` cruda |
| Errores HTTP | Mapear dominio→HTTP en un handler central (`@app.exception_handler`) |
| Errores de validación | Delegar en Pydantic (422) con detalle estructurado |
| Logs | Nunca loguear secrets ni tokens; correlación por `request_id` |

### Tests mínimos exigidos

| Nivel | Alcance mínimo | Framework |
|-------|----------------|-----------|
| Unitarios | Servicios, lógica de negocio, mapeo de errores | `pytest` |
| Integración | Endpoints con DB real (testcontainer), aislamiento tenant | `pytest` + `httpx` |
| Auth | Login, refresh, logout, expiración de tokens dual | `pytest` |

Cobertura mínima: **80%** en `src/` (excluyendo `tests/`). Todo `fix` llega con test de regresión.

---

## 2. TypeScript / React — Frontend (Noris)

### Estructura de carpetas

```
frontend/
├── src/
│   ├── main.tsx             # Bootstrap
│   ├── App.tsx              # Rutas raíz + guards
│   ├── api/                 # Cliente HTTP, interceptores de tokens
│   ├── components/          # Componentes reutilizables (atomic design)
│   ├── features/            # Módulos funcionales por dominio
│   │   └── <modulo>/
│   │       ├── components/  # Componentes del módulo
│   │       ├── hooks/       # Hooks específicos
│   │       └── api/         # Llamadas al backend del módulo
│   ├── hooks/               # Hooks transversales
│   ├── lib/                 # Utilidades puras, formateadores
│   ├── pages/               # Páginas = composición de features
│   ├── routes/              # Definición de rutas protegidas
│   └── types/               # Tipos compartidos
└── tests/                   # Tests Vitest/Playwright
```

### Naming

| Elemento | Convención | Ejemplo |
|----------|------------|---------|
| Componentes | `PascalCase` | `ProductCard.tsx` |
| Hooks | Prefijo `use` + PascalCase | `useProductos.ts` |
| Funciones/variables | `camelCase` | `formatoPrecio()` |
| Tipos/interfaces | `PascalCase` | `Producto` |
| Constantes | `SCREAMING_SNAKE_CASE` | `API_BASE_URL` |
| Archivos de componente | Igual que el componente | `ProductCard.tsx` |
| Clases CSS/Tailwind | Utilidades Tailwind + tokens de Nordanis (F0-1) | `bg-primary` según tokens |

### Manejo de errores

| Regla | Detalle |
|-------|---------|
| Estados de error | Todo fetch pasa por estados `loading / error / success` explícitos |
| Errores API | Parsear el JSON de error del contrato; mostrar mensaje accionable |
| Error boundaries | Un boundary por feature; nunca pantalla en blanco |
| Tokens | Interceptor maneja 401 → refresh transparente → reintento; logout en fallo de refresh |
| usuario final | Mensajes en español, sin jerga técnica |

### Tests mínimos exigidos

| Nivel | Alcance mínimo | Framework |
|-------|----------------|-----------|
| Unitarios | Utilidades, hooks, reducers | `vitest` |
| Componentes | Render de componentes clave, estados de error | `vitest` + Testing Library |
| E2E (desde Fase 1) | Flujos: login, CRUD producto, fiado | Playwright |

Cobertura mínima: **80%** en `src/`. Toda pantalla con estado de error tiene test de ese estado.

---

## 3. Go — operational-stream (Victor)

### Estructura de carpetas

```
operational-stream/
├── cmd/
│   └── operational-stream/
│       └── main.go         # Punto de entrada
├── internal/
│   ├── config/             # Config desde env
│   ├── ws/                 # Gestión WebSocket
│   ├── parser/             # Parsers de balanza (USB/RJ45/RS-232, M-15)
│   ├── ingest/             # Ingesta y validación de eventos
│   └── auth/               # Validación de tokens con backend
├── pkg/                    # Librerías usables externamente (mínimas)
├── go.mod
└── internal/tests/          # Tests
```

### Naming

| Elemento | Convención | Ejemplo |
|----------|------------|---------|
| Paquetes | `lowercase`, una palabra | `parser` |
| Archivos | `snake_case` | `balanza_rs232.go` |
| Funciones exportadas | `PascalCase` | `ParseFrame` |
| Funciones internas | `camelCase` | `parseWeight` |
| Constantes | `PascalCase` o `SCREAMING_SNAKE` | `MaxFrameSize` |
| Errores | `err` variables; sentencias error explícitas | `if err != nil` |
| Interfaces | Terminan en `-er` o describen contrato | `FrameParser` |

### Manejo de errores

| Regla | Detalle |
|-------|---------|
| Siempre explícito | `if err != nil { ... }` — nunca `_` sobre error |
| Wrapping | `fmt.Errorf("...: %w", err)` preservando cadena |
| Errores de dominio | `errors.Is` / `errors.As` con tipos sentinel (ej: `ErrFrameInvalido`) |
| Panics | Prohibidos fuera de `main` |
| Goroutines | Todo error en goroutine se reporta por canal/errgroup, nunca se descarta |
| Logs | Nunca loguear tokens ni payloads sensibles |

### Tests mínimos exigidos

| Nivel | Alcance mínimo | Framework |
|-------|----------------|-----------|
| Unitarios | Parsers (frames RS-232, USB, RJ45), validación de eventos | `go test` |
| Concurrency | Handlers WebSocket con `-race` | `go test -race` |
| Integración | Sesión completa cliente→ingesta (desde Fase 3) | `go test` |

Cobertura mínima: **80%** en `internal/`. Todo parser con tabla de casos (golden files de frames).

---

## 4. Docker / Infraestructura — DevOps (Alfredo)

### Estructura de carpetas

```
infra/
├── docker/
│   ├── docker-compose.yml         # Entorno base endurecido
│   ├── docker-compose.override.yml # Desarrollo local (no producción)
│   ├── Dockerfile.backend         # Multi-stage Python
│   ├── Dockerfile.frontend        # Multi-stage Node → Nginx
│   └── entrypoints/               # Scripts de arranque por servicio
├── nginx/                         # Reverse proxy / TLS
└── scripts/                       # Backup, restore, despliegue
```

### Naming

| Elemento | Convención | Ejemplo |
|----------|------------|---------|
| Servicios compose | `lowercase`, función clara | `api`, `frontend`, `db`, `operational-stream` |
| Redes | `lowercase`, ámbito | `internal`, `dmz` |
| Volúmenes | `<servicio>-<propósito>` | `db-data` |
| Imágenes | Etiqueta de versión fija, **nunca `latest`** | `postgres:16.4-alpine` |
| Secrets | Docker secrets, nunca variables en claro | `./secrets/` (fuera de git) |

### Manejo de errores

| Regla | Detalle |
|-------|---------|
| Healthchecks | Obligatorios en todos los servicios; dependencias con `depends_on: condition: service_healthy` |
| Entrypoints | `set -euo pipefail`; reintentos con backoff para dependencias |
| Falla de arranque | Log claro del servicio que falló y por qué; no silenciar con `restart` sin diagnóstico |
| Recursos | Límites `mem_limit` / `cpus` por servicio |

### Tests mínimos exigidos

| Nivel | Alcance mínimo | Herramienta |
|-------|----------------|-------------|
| Validación | `docker compose config` sin errores; imágenes build local OK | Docker Compose |
| Humo | Levantar stack completo → healthchecks en verde → login E2E | Script de humo |
| Seguridad | Sin puertos de DB expuestos; secrets montados, no ENV en claro (valida Lead_Blue) | Auditoría de compose |

Todo cambio de infraestructura requiere prueba de arranque en frío y de rebuild desde cero documentada.

---

## Checklist universal previo a merge

- [ ] Estructura de carpetas conforme a esta norma.
- [ ] Naming conforme a las tablas del área.
- [ ] Manejo de errores conforme a las reglas del área.
- [ ] Tests mínimos presentes y en verde; cobertura ≥ 80%.
- [ ] Ningún secret, token ni credencial en el código.
- [ ] Commits conventional con `Refs:` de la MAT.
- [ ] Tabla de observaciones incluida en la entrega (formato en `CONTRIBUTING.md`).

## Referencias

- `CONTRIBUTING.md` — flujo de ramas, commits, merge y reporte de observaciones.
- `docs/INTEGRACION-BACKEND-FRONTEND.md` — contrato de integración backend↔frontend.
- `docs/plantillas/` — plantillas para documentar endpoints, módulos e integraciones.
- `docs/MATRIZ-ASIGNACION.md` — tareas y refs.
