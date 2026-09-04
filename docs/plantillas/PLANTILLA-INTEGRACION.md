# Plantilla — Guía de Integración entre Componentes

> Usá esta plantilla para documentar toda integración entre componentes de BodegApp (ej: frontend↔backend, backend↔operational-stream, backend↔BCV, backend↔balanza serial, backend↔WhatsApp). Una integración sin esta guía es deuda técnica.

## Copiá este bloque y completalo

```markdown
# Integración <Componente A> ↔ <Componente B>

> **Ref tarea:** F<FASE>-XX · **Responsable A:** <nombre> · **Responsable B:** <nombre>
> **Tipo:** <API REST síncrona | WebSocket | scraping | serial | librería> · **Estado:** 🔴

## 1. Propósito

<Una línea: qué dato o capacidad fluye entre los componentes y para qué módulo.>

## 2. Contrato

### Si es API REST

| Método | Ruta | Request | Response | Doc completa |
|--------|------|---------|----------|--------------|
| POST | `/api/v1/<ruta>` | `<esquema>` | `<esquema>` | `docs/api/v1/<archivo>.md` |

### Si es WebSocket / serial / streaming

| Aspecto | Definición |
|---------|------------|
| Protocolo | <WS / RS-232 / USB / RJ45> |
| Formato de mensaje | <JSON/frame — esquema o referencia> |
| Dirección | <A→B, B→A, bidireccional> |
| Frecuencia/volumen | <estimación> |

## 3. Manejo de errores entre componentes

| Escenario | Componente que detecta | Comportamiento acordado | Referencia |
|-----------|----------------------|------------------------|------------|
| <Token inválido> | <backend> | <401 + código `TOKEN_INVALIDO`> | `docs/INTEGRACION-BACKEND-FRONTEND.md` |

## 4. Reintentos, timeouts y degradación

| Aspecto | Valor acordado |
|---------|---------------|
| Timeout | <ej: 5s> |
| Reintentos | <ej: 3 con backoff exponencial> |
| Degradación | <ej: cola local + reintento al recuperar> |

## 5. Seguridad

- [ ] Autenticación entre componentes definida (token / mTLS / red interna)
- [ ] Datos sensibles identificados y protegidos
- [ ] Revisado por Lead_Blue (ref: F0-07 / F4-02)

## 6. Plan de pruebas de integración

| Caso | Escenario | Responsable | Estado |
|------|-----------|-------------|--------|
| <INT-01> | <happy path> | <Emilio/nombre> | 🔴 |

## 7. Responsables de cambios

| Componente | Responsable de mantener esta guía |
|------------|--------------------------------|
| <A> | <nombre> |
```

## Reglas de las guías de integración

| Regla | Detalle |
|-------|---------|
| Ubicación | `docs/integracion/` — un archivo por integración |
| Acuerdo bilateral | La firma de esta guía es el acuerdo de contrato entre los dos responsables |
| Cambios | Todo cambio de contrato actualiza la guía en el mismo PR del código |
| Seguridad | Toda integración nueva pasa por revisión Lead_Blue antes de producción |
