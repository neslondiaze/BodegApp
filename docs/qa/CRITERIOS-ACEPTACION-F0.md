# BodegApp — Criterios de Aceptación Fase 0 (Checklist de Auditoría QA)

> **Ref**: F0-08 (anexo) · **Responsable**: Emilio (QA, Díaz Tech) · **Reporta a**: Cristian (Project Director)
> **Versión**: 1.0 — 03/09/2026
> **Uso**: este checklist ES la herramienta con la que QA audita las entregas de Fase 0 (F0-01..F0-08) antes de emitir el informe que habilita el merge a `main` (junto con validación de seguridad y autorización de Cristian, según PLAN-MAESTRO §5).
> **Regla de verificación**: cada criterio debe poder verificarse con un comando, un archivo o una observación reproducible. Nada se marca ✅ por estimación. Todo hallazgo se reporta con el formato obligatorio (Ref, Descripción, Severidad, Acción sugerida, ¿Bloquea producción?).

**Leyenda**: ✅ Cumple · ⚠️ Cumple parcialmente (observación) · ❌ No cumple (hallazgo) · ➖ No verificable aún / entregable no presentado

---

## A. F0-03 — Esquema PostgreSQL multi-tenant y aislamiento (Nelson)

Ámbito: `backend/` · Estrategia por decidir: schema-por-tenant vs RLS (aprobación de Cristian pendiente por diseño).

| # | Criterio verificable | Verificación | Estado |
|---|---------------------|---------------|--------|
| A1 | Existe propuesta técnica documentada comparando schema-por-tenant vs RLS, con recomendación fundamentada | Archivo en `backend/` (o docs de la propuesta) | ➖ |
| A2 | La propuesta fue aprobada explícitamente por Cristian antes de implementar | Registro de aprobación (MAT/chat) | ➖ |
| A3 | Existe esquema/migración versionada (reversible: `down` o equivalente probado) | Ejecutar migración + rollback en BD limpia | ➖ |
| A4 | Toda tabla de negocio tiene la clave de tenant (columna o equivalente según estrategia) con índice | Inspección del DDL | ➖ |
| A5 | Prueba automatizada demostrativa: sembrar datos de 2 tenants, ejecutar consultas con tenant A y verificar cero filas de B | Ejecutar suite de aislamiento en CI | ➖ |
| A6 | Si RLS: políticas con `FORCE` y prueba de que owner/superusuario conectado como tenant no ve datos ajenos | Prueba dedicada de bypass | ➖ |
| A7 | Si schema-por-tenant: prueba de que una conexión mal enrutada no cae en el esquema incorrecto | Prueba de enrutamiento | ➖ |
| A8 | Montos de dinero definidos como `NUMERIC` (no float) desde el día uno | Inspección del DDL | ➖ |
| A9 | Identificadores no secuenciales/expuestos entre tenants (UUID o equivalente) | Inspección del DDL | ➖ |

**Veredicto A**: ➖ Pendiente de entrega (límite 12/09/2026).

---

## B. F0-04 — Autenticación JWT RS256 + tokens dual (Nelson)

Ámbito: `backend/`

| # | Criterio verificable | Verificación | Estado |
|---|---------------------|---------------|--------|
| B1 | Emisión y verificación de tokens con algoritmo RS256 (par de claves asimétricas) | Ejecutar suite auth en CI | ➖ |
| B2 | Token firmado con clave privada correcta pasa; firmado con clave ajena → 401 | Prueba negativa automatizada | ➖ |
| B3 | Rechazo de `alg=none` y de tokens HS256 (confusion attack) | Prueba negativa automatizada | ➖ |
| B4 | Token expirado → 401; leeway de reloj acotado y documentado | Prueba con reloj simulado | ➖ |
| B5 | Semántica de tokens dual (contratante/trabajo) documentada: campos, vigencias, capacidades de cada tipo | Documento + código | ➖ |
| B6 | El token de trabajo NO puede ejecutar operaciones administrativas del contratante (prueba negativa por endpoint crítico) | Matriz de acceso automatizada | ➖ |
| B7 | El tenant queda contenido en el token y el backend lo valida contra el recurso solicitado (base de TR-01) | Prueba de consistencia token-recurso | ➖ |
| B8 | Rotación/refresh de tokens con revocación efectiva (logout invalida) | Prueba de ciclo de vida | ➖ |
| B9 | Claves privadas NUNCA en el repositorio (secrets por gestión de Docker/env) | gitleaks en verde; revisión | ➖ |
| B10 | Cobertura de la suite auth ≥ 95 % | Reporte de cobertura en CI | ➖ |

**Veredicto B**: ➖ Pendiente de entrega (límite 15/09/2026).

---

## C. F0-05 — Scaffold frontend React 19 + Vite + Tailwind + routing protegido + tokens dual (Noris)

Ámbito: `frontend/`

| # | Criterio verificable | Verificación | Estado |
|---|---------------------|---------------|--------|
| C1 | `npm ci` + `npm run build` reproducibles en entorno limpio, sin errores | Ejecutar en contenedor/CI limpio | ➖ |
| C2 | React 19, Vite y Tailwind en las versiones del stack (package.json verificable) | Inspección de `package.json` | ➖ |
| C3 | Ruta protegida: sin token → redirige a login; nunca renderiza el contenido | Prueba Vitest/Playwright | ➖ |
| C4 | Token inválido/expirado → expulsión limpia del área protegida, sin pantalla rota | Prueba E2E | ➖ |
| C5 | Arquitectura de tokens dual presente en el cliente: almacenamiento, selección y envío del token correcto por tipo de operación | Revisión de código + prueba | ➖ |
| C6 | Almacenamiento de tokens con decisión documentada y segura (memoria/cookie httpOnly si el backend la ofrece; localStorage solo si Lead_Blue la aprueba) | Revisión + visto de seguridad | ➖ |
| C7 | Consumo del design system de Nordanis (F0-01) o marcador explícito de integración pendiente sin inventar tokens propios | Inspección de tokens Tailwind | ➖ |
| C8 | Suite Vitest mínima en verde en CI (routing protegido incluido) | Pipeline | ➖ |
| C9 | Sin secrets ni claves en el bundle | Inspección del bundle + gitleaks | ➖ |
| C10 | Lint y typecheck en verde | `npm run lint` + `tsc --noEmit` | ➖ |

**Veredicto C**: ➖ Pendiente de entrega (límite 15/09/2026).

---

## D. F0-02 / F0-07 — Docker endurecido Sentinel Shield v1.0 + aprobación Zero Trust (Alfredo + Lead_Blue)

Ámbito: `infra/docker/` (y compose raíz si aplica)

| # | Criterio verificable | Verificación | Estado |
|---|---------------------|---------------|--------|
| D1 | El diseño Zero Trust fue revisado y aprobado por Lead_Blue (F0-07) ANTES de implementar | Registro de aprobación | ➖ |
| D2 | `docker compose up` desde clon limpio levanta API, Frontend y PostgreSQL y los tres quedan healthy | Ejecutar smoke con healthchecks | ➖ |
| D3 | Redes segmentadas: PostgreSQL no publica puertos al host; solo la API/Frontend exponen lo mínimo | `docker compose config` + `ss`/`nmap` | ➖ |
| D4 | Gestión de secrets de Docker usada (sin contraseñas en texto plano en el compose ni en el repo) | Inspección + gitleaks | ➖ |
| D5 | Imágenes fijadas por tag específico o digest (prohibido `latest`) | `docker compose config` | ➖ |
| D6 | Contenedores corren como usuario no-root | `docker inspect` / Dockerfile USER | ➖ |
| D7 | Healthchecks definidos en los tres servicios | `docker compose config` | ➖ |
| D8 | Límites de recursos (memoria/CPU) y política de reinicio definidos | `docker compose config` | ➖ |
| D9 | trivy sin CVE críticas en las imágenes usadas | `trivy image` por imagen | ➖ |
| D10 | gitleaks sin hallazgos en el repositorio | Ejecutar en CI | ➖ |
| D11 | Volúmenes con respaldo/durabilidad definidos para datos de PostgreSQL (el dinero de los fiados vive ahí) | Inspección de volúmenes | ➖ |
| D12 | Documentación del entorno: cómo levantar, variables requeridas, qué hace cada servicio | README en `infra/` | ➖ |

**Veredicto D**: ➖ Pendiente de entrega (límite 10/09/2026 — primer gate de la fase).

---

## E. F0-01 — Design system (Nordanis) — verificación QA funcional

Ámbito: `design/` · Nota: QA no valida estética (dominio del inversor/Nordanis); valida trazabilidad y usabilidad técnica.

| # | Criterio verificable | Verificación | Estado |
|---|---------------------|---------------|--------|
| E1 | Tokens de color claros/oscuros EXACTOS a §4 de REQUERIMIENTOS (hexadecimal por hexadecimal) | Comparación contra tabla §4 | ➖ |
| E2 | Tipografías: Plus Jakarta Sans o Cabinet Grotesk (headlines), Inter o SF Pro Display (body) | Inspección de tokens | ➖ |
| E3 | Contraste AA (WCAG) verificado para las combinaciones texto/fondo en ambos modos | Medición automatizada | ➖ |
| E4 | Tokens exportables a Tailwind (formato consumible por F0-05) | Prueba de integración con frontend | ➖ |
| E5 | Análisis de `design/referencias/modelo-referencia.png` documentado | Documento en `design/` | ➖ |

**Veredicto E**: ➖ Pendiente de entrega (límite 08/09/2026 — primera entrega de la fase).

---

## F. F0-06 / F0-08 — Documentación y plan de pruebas

| # | Criterio verificable | Verificación | Estado |
|---|---------------------|---------------|--------|
| F1 | Estructura documental de Carlos (F0-06) presente: README raíz, guía de contribución, estándares por área | Inspección de `docs/` | ➖ |
| F2 | Plan maestro de pruebas (F0-08) presente y trazable a módulos y fases | `qa/PLAN-MAESTRO-PRUEBAS.md` | ✅ (este anexo lo completa) |
| F3 | Criterios de aceptación F0 publicados | `docs/qa/CRITERIOS-ACEPTACION-F0.md` | ✅ (este documento) |

**Veredicto F**: ✅ F0-08 cumplido; F0-06 pendiente de entrega (límite 12/09/2026).

---

## Protocolo de auditoría

1. **Orden de auditoría por riesgo**: D (docker/Zero Trust) → A (aislamiento) → B (auth) → C (frontend) → E (design) → F (docs). El orden responde al mapa de riesgo de `qa/PLAN-MAESTRO-PRUEBAS.md` §3.
2. **Ciclo por entregable**: recepción en rama → verificación de criterios → informe de auditoría con formato obligatorio (todo hallazgo se reporta) → re-test si hubo hallazgos → informe final que habilita o no el gate de merge.
3. **Criterio de aprobación del entregable**: 100 % de criterios ✅; se toleran ⚠️ solo si no afectan riesgo crítico y quedan como acción registrada.
4. **Criterio de aprobación de FASE 0**: todos los entregables auditados y aprobados, sin hallazgos Críticos/Bloqueantes abiertos → informe QA de F0 a Cristian.
5. **Riesgo conocido a la fecha de emisión**: los estados están en ➖ porque a la fecha (03/09/2026) ningún entregable F0 se ha presentado; las fechas límite más próximas son E (08/09) y D (10/09). El gate F0→F1 depende íntegramente de su cumplimiento.

---

*Fin del documento. Emilio — QA, Díaz Tech.*
