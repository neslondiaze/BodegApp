# Contribuir a BodegApp

Guía obligatoria de flujo de trabajo para todo subagente del equipo Díaz Tech. Aplica desde Fase 0. Fuente de gobernanza: `docs/PLAN-MAESTRO.md` (propiedad de Cristian, Project Director).

## Ruta rápida

1. Leé `docs/REQUERIMIENTOS.md` y `docs/MATRIZ-ASIGNACION.md` (tu tarea).
2. Creá tu rama: `feature/<area>-<ref>` (ej: `feature/backend-F0-03`).
3. Trabajá con conventional commits (una unidad lógica por commit).
4. Al terminar: verificá lint + tests, subí tu rama y reportá observaciones con el formato obligatorio.
5. El merge a `main` lo ejecuta **solo Cristian** con `--no-ff`, previo QA ✅ y seguridad ✅.

## 1. Flujo de ramas

| Regla | Detalle |
|-------|---------|
| Nomenclatura | `feature/<area>-<ref-de-tarea>` — ej: `feature/frontend-F0-05`, `feature/devops-F0-02` |
| Área | Coincide con tu rol en la MAT: `backend`, `frontend`, `go`, `devops`, `uiux`, `docs`, `qa`, `design`, `security`, `reports` |
| Ref | Código de la MATRIZ-ASIGNACION (ej: `F0-03`, `F1-07`, `T-01`) |
| Vida útil | Una rama = una tarea de la MAT. Si la tarea crece, proponé dividirla antes que ensanchar la rama |
| Sincronización | Rebase sobre `main` reciente antes de solicitar merge |

### Prefijos de área por subagente

| Subagente | Prefijo |
|-----------|---------|
| Nelson (Backend) | `feature/backend-*` |
| Noris (Frontend) | `feature/frontend-*` |
| Alfredo (DevOps) | `feature/devops-*` |
| Nordanis (UI/UX) | `feature/uiux-*` |
| Victor (Go) | `feature/go-*` |
| Carlos (Documentación) | `feature/docs-*` |
| Emilio (QA) | `feature/qa-*` |

## 2. Convención de commits (Conventional Commits)

Formato obligatorio:

```
<tipo>(<área>): <descripción imperativa, máx. 72 caracteres>

[Cuerpo opcional: qué y por qué, no cómo.]

Refs: <ref-de-tarea>
```

| Tipo | Uso |
|------|-----|
| `feat` | Nueva funcionalidad |
| `fix` | Corrección de defecto |
| `docs` | Solo documentación |
| `refactor` | Cambio que no altera comportamiento |
| `test` | Adición/corrección de pruebas |
| `perf` | Mejora de rendimiento |
| `style` | Formato, sin cambio lógico |
| `chore` | Mantenimiento (deps, tooling) |
| `ci` | Pipeline CI |
| `build` | Sistema de build / imagen Docker |
| `security` | Endurecimiento de seguridad (extensión del proyecto) |

Ejemplos:

```
feat(backend): endpoint de login con tokens dual RS256

Refs: F0-04
```

```
fix(frontend): corrige expiración silenciosa del token de trabajo

El interceptor no reintentaba tras 401 con token vencido.

Refs: F0-05
```

## 3. Protección de `main`

| Regla | Detalle |
|-------|---------|
| Prohibido | Push directo a `main` por cualquier subagente. Sin excepciones. |
| Propietario | `main` es propiedad exclusiva de Cristian (Project Director). |
| Requisitos de merge | Informe QA de Emilio ✅ + validación seguridad Lead_Blue/Lead_Red ✅ + autorización de Cristian. |
| Protocolo de merge (ejecuta Cristian) | `git checkout main` → `git merge <rama> --no-ff -m "Merge: Agente Líder integra <Tarea> de <Subagente>"` → `git push origin main` |

El flag `--no-ff` es obligatorio: preserva el historial de ramas y la trazabilidad de quién integró qué.

## 4. Formato obligatorio de reporte de observaciones

Directiva del inversor: **todo hallazgo se reporta, sin importar cuán mínimo parezca.** Cada entrega (PR, informe de tarea, reporte de QA o seguridad) incluye una tabla de observaciones con estas columnas exactas:

| Ref | Descripción | Severidad | Acción sugerida | ¿Bloquea producción? |
|-----|-------------|-----------|-----------------|---------------------|

- **Ref**: identificador único secuencial de la observación (ej: `OBS-001`) o referencia a la tarea/documento afectado.
- **Descripción**: hallazgo concreto y verificable, sin calificativos.
- **Severidad**: `Crítica` | `Alta` | `Media` | `Baja` | `Informativa`.
- **Acción sugerida**: corrección o mitigación propuesta, accionable.
- **¿Bloquea producción?**: `Sí` / `No`. Solo `Crítica` y `Alta` pueden justificar `Sí`, con justificación explícita.

### Escala de severidad

| Severidad | Criterio |
|-----------|----------|
| Crítica | Falla de seguridad, pérdida de datos o bloqueo total de una función |
| Alta | Función degradada o requisito del inversor incumplido |
| Media | Desviación de estándares, deuda técnica con impacto operativo |
| Baja | Detalle cosmético o mejora menor |
| Informativa | Nota para decisión futura, sin acción inmediata |

### Ejemplo

| Ref | Descripción | Severidad | Acción sugerida | ¿Bloquea producción? |
|-----|-------------|-----------|-----------------|---------------------|
| OBS-001 | `docker-compose.yml` expone el puerto 5432 de PostgreSQL fuera de la red interna | Crítica | Enlazar PostgreSQL solo a la red `internal` y eliminar el mapeo de puertos público | Sí |

## 5. Bloqueos

Si tu tarea se traba: marcá 🟠 tu fila en `docs/MATRIZ-ASIGNACION.md` con nota de quién/qué la traba y reportá a Cristian. No esperes a la fecha límite.

## Verificación previa a solicitar merge

- [ ] Rama nombrada `feature/<area>-<ref>`.
- [ ] Commits conventional con `Refs:` de la tarea.
- [ ] Lint y tests en verde localmente.
- [ ] Documentación afectada actualizada (plantillas de `docs/plantillas/` si aplica).
- [ ] Tabla de observaciones incluida en la entrega.
- [ ] No hay secrets ni credenciales en el diff.
