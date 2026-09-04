# Plantilla — Especificación de Módulo Funcional

> Usá esta plantilla para especificar cada módulo funcional de `docs/REQUERIMIENTOS.md` (M-01 a M-15) **antes** de implementar. Un módulo no entra a desarrollo sin esta especificación aprobada por Cristian.

## Copiá este bloque y completalo

```markdown
# Módulo <M-XX> — <Nombre>

> **Ref requerimiento:** M-XX · **Ref tarea MAT:** F<FASE>-XX · **Fase:** <n>
> **Responsable backend:** <nombre> · **Responsable frontend:** <nombre> · **Estado:** 🔴

## 1. Definición funcional

<2-4 líneas: qué resuelve este módulo para el negocio de la bodega. Trazado directo al requerimiento.>

## 2. Alcance

### Dentro de alcance
- <Funcionalidad incluida>

### Fuera de alcance
- <Explícitamente excluido y por qué>

## 3. Reglas de negocio

| # | Regla | Fuente |
|---|-------|--------|
| R1 | <Regla concreta y verificable> | Requerimiento §, inversor |

## 4. Modelo de datos (si aplica)

| Campo | Tipo | Obligatorio | Reglas |
|-------|------|-------------|--------|
| <nombre> | <tipo> | Sí/No | <restricciones> |

## 5. Endpoints del módulo

| Método | Ruta | Propósito | Doc endpoint |
|--------|------|-----------|--------------|
| POST | `/api/v1/<ruta>` | <propósito> | `docs/api/v1/<archivo>.md` |

## 6. Pantallas del módulo

| Pantalla | Propósito | Responsable |
|----------|-----------|-------------|
| <Nombre> | <propósito> | <nombre frontend> |

## 7. Criterios de aceptación

- [ ] <Criterio verificable por QA (Emilio), no ambiguo>
- [ ] <Criterio>

## 8. Dependencias y riesgos

| Tipo | Descripción | Ref |
|------|-------------|-----|
| Dependencia | <De qué tarea depende> | F0-XX |
| Riesgo | <Riesgo conocido> | — |
```

## Reglas de la especificación de módulos

| Regla | Detalle |
|-------|---------|
| Trazabilidad | Todo M-XX de `docs/REQUERIMIENTOS.md` tiene su especificación en `docs/modulos/M-XX-<nombre>.md` |
| Antes de codificar | La especificación se aprueba antes de que Nelson/Noris inicien la tarea |
| Criterios medibles | Cada criterio de aceptación debe poder marcarse ✅/❌ por QA sin interpretación |
| Cambios | Cambio de regla de negocio = cambio de esta doc en el mismo PR del código |
