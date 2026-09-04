# Plantilla — Documentación de Endpoint

> Usá esta plantilla para documentar cada endpoint de la API (`backend/`). Completala al implementar y mantenela actualizada ante cualquier cambio de contrato. Ubicación sugerida: `docs/api/<version>/<recurso>.md`.

## Copiá este bloque y completalo por endpoint

```markdown
# <MÉTODO> /api/v1/<recurso>[/<sub-recurso>]

> **Ref módulo:** M-XX · **Ref tarea:** F1-XX · **Responsable:** <nombre> · **Estado:** 🟡

## Propósito

<Una línea: qué hace este endpoint y para qué módulo del negocio.>

## Autenticación

- [ ] Requiere token de trabajo (access, corta duración)
- [ ] Requiere token contratante (refresh, larga duración) — solo endpoints de sesión
- [ ] Público

## Request

### Parámetros

| Ubicación | Nombre | Tipo | Obligatorio | Descripción |
|-----------|--------|------|-------------|-------------|
| path | `id` | UUID | Sí | Identificador del producto |
| query | `page` | int | No | Página (default 1) |

### Cuerpo (si aplica)

\`\`\`json
{
  "nombre": "Harina de maíz 1kg",
  "precio_bs": 150.50
}
\`\`\`

## Response

### Éxito — `<código>`

\`\`\`json
{
  "id": "uuid",
  "nombre": "Harina de maíz 1kg"
}
\`\`\`

### Errores

| Código | Código interno | Cuándo ocurre |
|--------|---------------|---------------|
| 400 | `VALIDATION_ERROR` | Cuerpo malformado |
| 401 | `TOKEN_INVALIDO` | Token ausente o vencido |
| 404 | `RECURSO_NO_ENCONTRADO` | El id no existe en el tenant |

## Reglas de negocio y validaciones

- <Regla: ej: precio > 0, fecha de pago no anterior a hoy.>

## Multi-tenant

- Aislamiento: <cómo se garantiza que el resultado solo contenga datos del tenant autenticado.>

## Tests que lo cubren

- <Archivo y caso: ej: `tests/productos/test_create.py::test_crear_producto_ok`.>
```

## Reglas de la documentación de endpoints

| Regla | Detalle |
|-------|---------|
| Granularidad | Un bloque por endpoint; un archivo por recurso (`productos.md`, `fiados.md`) |
| Versionado | Los archivos viven en `docs/api/v1/`; una nueva versión de API = nueva carpeta |
| Contrato primero | Ningún endpoint se expone a Noris sin este documento aprobado |
| Errores | Listar **todos** los códigos que el endpoint puede devolver, con el formato del contrato (`docs/INTEGRACION-BACKEND-FRONTEND.md`) |
| Cambios | Todo cambio de contrato actualiza esta doc **en el mismo PR** que el código |
