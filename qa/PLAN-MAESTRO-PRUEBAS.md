# BodegApp — Plan Maestro de Pruebas

> **Ref**: F0-08 · **Responsable**: Emilio (QA, Díaz Tech) · **Reporta a**: Cristian (Project Director)
> **Versión**: 1.0 — 03/09/2026 · **Estado**: documento vivo; se ajusta al cierre de cada fase.
> **Trazabilidad**: módulos M-01..M-15 (`docs/REQUERIMIENTOS.md`) · fases 0-4 (`docs/PLAN-MAESTRO.md`) · tareas (`docs/MATRIZ-ASIGNACION.md`).
> Criterios de auditoría de Fase 0: `docs/qa/CRITERIOS-ACEPTACION-F0.md`.

---

## 1. Objetivo y alcance

Definir la estrategia, la matriz de pruebas por módulo, la priorización por riesgo y el Definition of Done que rige toda la actividad de QA del proyecto, desde Fase 0 hasta el despliegue a producción.

Alcance: los 15 módulos funcionales (M-01..M-15), los componentes transversales (autenticación, aislamiento multi-tenant, infraestructura Docker, microservicio Go) y las fases 0 a 4 del plan maestro.

No está en el alcance de QA: la autorización final de merges (Cristian) ni la ejecución del pentest (Lead_Red), aunque QA audita sus criterios de entrada y salida.

---

## 2. Estrategia general de pruebas

### 2.1 Principios rectores

1. **Riesgo primero**: el esfuerzo de prueba se asigna por riesgo de negocio, no por orden de módulo ni por comodidad del calendario.
2. **El aislamiento se demuestra, no se supone**: cada módulo hereda la batería de pruebas cruzadas entre tenants (TR-01). Ningún módulo se aprueba sin ella.
3. **El dinero se prueba con profundidad**: fiados exigen pruebas unitarias, de propiedad, integración, concurrencia y E2E. Es el nivel más alto de rigor del proyecto.
4. **Lo externo se simula antes de probarse en vivo**: BCV, WhatsApp y balanzas se prueban con contratos y fixtures; en vivo solo en UAT/pre-producción.
5. **Todo hallazgo se reporta** (directiva del inversor), sin importar cuán menor parezca. Severidad y bloqueo se evalúan por separado.

### 2.2 Tipos de prueba

| Tipo | Qué valida | Cuándo | Herramientas | Responsable primario |
|------|-----------|--------|--------------|---------------------|
| Unitarias | Lógica de negocio aislada (cálculos, validaciones, parsers) | Continuo, en cada tarea | pytest, Vitest, go test | Cada desarrollador |
| Integración | Módulos contra PostgreSQL real, contratos de API, aislamiento | En cada tarea de backend/frontend | pytest + httpx + testcontainers, MSW | Desarrollador + QA |
| E2E | Flujos completos de usuario multi-paso (login → operación → resultado) | Fin de cada fase y en cada flujo crítico | Playwright (Chromium, Firefox, WebKit) | QA |
| Seguridad | Vulnerabilidades conocidas y superficie de ataque | Continuo (automático) + pentest en F4 | trivy, gitleaks, bandit, gosec, ZAP baseline; pentest manual (Lead_Red, F4-01) | Blue Team + QA |
| UAT | Validez de negocio con escenarios reales de bodega | F4-05, con acceso anticipado de usuarios piloto desde F2 | Checklists guiados, sesiones grabadas | QA + inversor/usuarios |
| Rendimiento (complementario) | Concurrencia y estabilidad bajo carga | F2 (fiados) y F4 (integral) | k6 | QA + Alfredo (DevOps) |

### 2.3 Herramientas por área

| Área | Unitarias | Integración | E2E / UI | Seguridad |
|------|-----------|-------------|----------|-----------|
| Backend (FastAPI, Python 3.12) | pytest, pytest-asyncio, hypothesis (propiedades aritméticas de fiados) | httpx AsyncClient, testcontainers-python (PostgreSQL real), schemathesis (fuzzing del contrato OpenAPI) | — | bandit, pip-audit |
| Frontend (React 19 + Vite + Tailwind) | Vitest + React Testing Library | MSW (APIs simuladas) | Playwright + axe-core (accesibilidad) | npm audit |
| operational-stream (Go) | go test (stdlib, tabla de casos) | httptest + clientes WebSocket de prueba, `-race` obligatorio | Playwright (flujos que consumen el stream) | gosec, govulncheck |
| Infraestructura (Docker) | — | Smoke de compose, healthchecks | — | trivy (imágenes), gitleaks (secrets), hadolint (Dockerfiles), ZAP baseline |
| Datos / migraciones | Pruebas de migración reversibles | Fixtures multi-tenant deterministas | — | — |

Reglas fijas de herramientas: los montos de dinero se prueban con `Decimal`/`NUMERIC` (prohibido float en pruebas y en implementación); toda prueba de aislamiento usa dos tenants sembrados reales, no mocks del filtro.

### 2.4 Entornos de prueba

| Entorno | Propósito | Datos | Restricciones |
|---------|----------|-------|---------------|
| DEV | Desarrollo local, hot reload | Sintéticos efímeros | BCV y WhatsApp simulados por fixtures |
| CI (GitHub Actions) | Gates automáticos por PR | Generados por las suites | Sin red externa salvo dependencias de build |
| QA (staging interno) | Integración, E2E y regresión del equipo QA | 3+ tenants sembrados por script determinista (propietario: QA) | BCV vía proxy simulado; WhatsApp sandbox |
| UAT / Pre-producción | Validación de negocio y pruebas en vivo | Datos sembrados o copia anonimizada | Scraping BCV real; plantillas WhatsApp aprobadas |
| PROD | Operación | Reales | Solo smoke post-despliegue + monitoreo (T-05) |

### 2.5 Umbrales de calidad (bloquean el pipeline)

| Área | Umbral mínimo |
|------|---------------|
| Backend de dinero (M-08, M-09) + auth/aislamiento (TR-01, TR-02) | ≥ 95 % cobertura de líneas |
| Resto del backend | ≥ 85 % cobertura de líneas |
| Frontend (componentes/hooks) | ≥ 70 % + E2E obligatorio de cada flujo crítico |
| Go | `go test ./... -race` en verde |
| Contenedores | 0 CVE críticas (trivy) · 0 secrets (gitleaks) |
| Accesibilidad | 0 violaciones críticas de axe en flujos nuevos |

---

## 3. Priorización basada en riesgo

### 3.1 Metodología

**Riesgo = Impacto en el negocio × Probabilidad de fallo.**

- **Impacto** (orden decreciente): dinero del cliente > datos personales/cumplimiento legal > integridad operativa > reputación > comodidad.
- **Probabilidad**: dependencia externa, concurrencia, complejidad del dominio, heterogeneidad de hardware.

Niveles: CRÍTICO (prueba con profundidad máxima y gate personal de QA), ALTO (prueba profunda), MEDIO (prueba estándar).

### 3.2 Mapa de riesgo de negocio

| # | Riesgo | Módulos | Impacto | Probabilidad | Nivel |
|---|--------|---------|---------|--------------|-------|
| 1 | Fuga de datos entre tenants | Todos (transversal TR-01) | Datos financieros y personales de cada bodega expuestos; daño legal y reputacional irreversible | Media: un solo endpoint sin filtro basta | **CRÍTICO** |
| 2 | Fiados: dinero del cliente | M-08, M-09 | Error aritmético o de concurrencia = dinero perdido del cliente; es la operación central del negocio | Media: precisión decimal + abonos concurrentes | **CRÍTICO** |
| 3 | Autenticación y tokens dual | Transversal TR-02 | Control de acceso total al sistema | Media | **CRÍTICO** |
| 4 | Scraping BCV: dependencia externa frágil | M-10..M-13 | Los precios de toda la bodega dependen de la tasa; el BCV cambia su HTML, cae o bloquea sin aviso, sin API oficial | Alta | **CRÍTICO** |
| 5 | Integridad de inventario | M-02, M-06, M-07 | Compras y alertas se calculan del stock; stock corrupto = compras equivocadas | Media | ALTO |
| 6 | Promociones WhatsApp | M-14 | Canal comercial masivo y visible; errores llegan a todos los clientes + cumplimiento de opt-out | Media: aprobaciones externas de Meta | ALTO |
| 7 | Balanza serial heterogénea | M-15 | Peso erróneo = precio erróneo en el momento de la venta | Alta: diversidad de protocolos | ALTO |
| 8 | Lectores de códigos | M-04, M-05 | Fricción operativa (existe alternativa manual de alta) | Media | MEDIO |
| 9 | Configuración tienda/proveedores | M-01, M-03 | Sin pérdida directa de dinero | Baja | MEDIO |

### 3.3 Orden de ejecución — qué se prueba primero y por qué

| Orden | Qué se prueba | Por qué | Fase |
|-------|---------------|---------|------|
| 0 | Auditoría de entregables con `docs/qa/CRITERIOS-ACEPTACION-F0.md` | Sin fundaciones auditadas, todo lo demás se prueba dos veces y se prueba tarde | F0 |
| 1 | Arnés automatizado de aislamiento (TR-01) y auth (TR-02) | Se construye una vez y lo heredan los 15 módulos; cubre los riesgos 1 y 3 en cada entrega futura | F0/F1 |
| 2 | M-02 CRUD Productos | Base de todo el inventario; primer consumidor del arnés de aislamiento | F1 |
| 3 | M-06 alertas + M-07 reporte de compras | Alimentan decisiones de gasto del bodeguero | F1 |
| 4 | M-03 y M-01 (CRUDs de soporte) | Completan el núcleo F1 con esfuerzo de prueba estándar | F1 |
| 5 | M-08/M-09 fiados con profundidad máxima (unitarias + propiedad + integración + concurrencia + E2E) | Dinero del cliente: riesgo máximo del producto. Diseño de casos comienza en F1 para ejecutar en F2 sin demora | F2 |
| 6 | M-10..M-13 BCV (contract tests con fixtures HTML + simulación de fallos) | Dependencia frágil: el fallo silencioso es el peor escenario (precios corruptos) | F2 |
| 7 | M-14 WhatsApp | Trámites de Meta con lead time; pruebas con sandbox primero | F2 |
| 8 | M-04/M-05/M-15 + operational-stream | Mocks y fixtures primero; laboratorio de hardware después | F3 |
| 9 | Pentest, UAT integral, carga y despliegue | Endurecimiento final con todo integrado | F4 |

### 3.4 Profundidad obligatoria por prioridad

| Prioridad | Profundidad mínima |
|-----------|-------------------|
| **Crítica** | Unitarias + integración + E2E + casos de concurrencia + pruebas de propiedad. Emilio audita y ejecuta personalmente el re-test antes de emitir informe de merge |
| **Alta** | Unitarias + integración + E2E del happy path + casos borde principales |
| **Media** | Unitarias + integración + smoke E2E |

---

## 4. Matriz de pruebas por módulo

### 4.1 Resumen (M-01..M-15 + transversales)

| Ref | Módulo | Fase | Tareas MAT asociadas | Prioridad QA | Riesgo dominante |
|-----|--------|------|---------------------|--------------|------------------|
| M-01 | Configuración de Tienda | F1 | F1-03, F1-05 | Media | Configuración por tenant |
| M-02 | CRUD Productos | F1 | F1-01, F1-05 | Alta | Integridad de inventario + aislamiento |
| M-03 | CRUD Proveedores | F1 | F1-02, F1-05 | Media | Aislamiento |
| M-04 | Lector código de barras | F3 | F3-01 | Media | Fiabilidad de escaneo |
| M-05 | Lector QR | F3 | F3-01 | Media | Fiabilidad de escaneo |
| M-06 | Alerta mínimo de productos | F1 | F1-04, F1-06 | Alta | Disparo correcto sin spam |
| M-07 | Reporte de compras | F1 | F1-07, F1-08 | Alta | Cálculo correcto → gasto |
| M-08 | CRUD Fiados | F2 | F2-01, F2-05 | **Crítica** | Dinero del cliente |
| M-09 | Historial de fiados | F2 | F2-02, F2-05 | **Crítica** | Dinero + auditoría legal |
| M-10 | Scraping BCV | F2 | F2-03 | **Crítica** | Dependencia externa frágil |
| M-11 | Actualización dólar BCV | F2 | F2-03 | Alta | Propagación de tasa |
| M-12 | Historial tipo de cambio | F2 | F2-03, F2-05 | Alta | Inmutabilidad del histórico |
| M-13 | Configuración de scraping | F2 | F2-04, F2-06 | Alta | Scheduler que falla en silencio |
| M-14 | Promociones WhatsApp | F2 | F2-07, F2-08, F2-09 | Alta | Canal masivo + cumplimiento legal |
| M-15 | Integración balanza | F3 | F3-03, F3-04 | Alta | Hardware heterogéneo |
| TR-01 | Aislamiento multi-tenant | F0+ | F0-03 (y todos) | **Crítica** | Fuga de datos |
| TR-02 | Auth JWT RS256 + tokens dual | F0+ | F0-04, F0-05 | **Crítica** | Control de acceso |
| TR-03 | Docker / Zero Trust | F0+ | F0-02, F0-07 | **Crítica** | Superficie de ataque |
| TR-04 | operational-stream (Go) | F3 | F3-02, F3-05 | Alta | Tiempo real |
| TR-05 | Flujos E2E de negocio | F1-F2 | — | Alta | Integración total |

### 4.2 Detalle de casos críticos por módulo

#### M-01 — Configuración de Tienda (Fase 1 · Prioridad: Media)

| ID | Caso crítico | Tipo |
|----|-------------|------|
| TC-M01-01 | Crear y actualizar datos de la tienda persiste correctamente por tenant | Integración |
| TC-M01-02 | Tenant B no puede leer ni editar la configuración del tenant A (404, sin revelar existencia) | Integración |
| TC-M01-03 | Validaciones de campos obligatorios y formatos (nombre, RIF, teléfono, moneda) | Unitaria |
| TC-M01-04 | Tenant nuevo nace con valores por defecto operables | Integración |

#### M-02 — CRUD Productos (Fase 1 · Prioridad: Alta)

| ID | Caso crítico | Tipo |
|----|-------------|------|
| TC-M02-01 | Alta de producto con todos los campos obligatorios | Integración |
| TC-M02-02 | Consulta, modificación y borrado de producto | Integración |
| TC-M02-03 | Código de barras duplicado dentro del tenant rechazado; el mismo código en otro tenant es permitido | Integración |
| TC-M02-04 | Aislamiento: listado y búsqueda del tenant A nunca incluyen productos del tenant B | Integración |
| TC-M02-05 | Stock y stock mínimo: validación de rangos según regla definida (negativos prohibidos o justificados) | Unitaria |
| TC-M02-06 | Concurrencia: dos actualizaciones simultáneas de stock no corrompen el valor final | Integración |
| TC-M02-07 | Volumen: paginación y búsqueda con 1.000+ productos responde en < 500 ms | Rendimiento |
| TC-M02-08 | Borrado de producto con referencias (fiados, reportes) respeta integridad referencial | Integración |
| TC-M02-09 | Búsqueda por nombre/código con acentos y mayúsculas (mercado venezolano: "Café", "CAFE") | Unitaria |

#### M-03 — CRUD Proveedores (Fase 1 · Prioridad: Media)

| ID | Caso crítico | Tipo |
|----|-------------|------|
| TC-M03-01 | CRUD completo de proveedores | Integración |
| TC-M03-02 | Aislamiento entre tenants en todas las rutas | Integración |
| TC-M03-03 | Borrado de proveedor con productos asociados sigue regla definida (bloqueo o cascada) sin huérfanos | Integración |

#### M-04 — Lector código de barras (Fase 3 · Prioridad: Media)

| ID | Caso crítico | Tipo |
|----|-------------|------|
| TC-M04-01 | Decodifica EAN-13, EAN-8 y UPC-A válidos | Unitaria |
| TC-M04-02 | Código con checksum inválido se rechaza con mensaje claro | Unitaria |
| TC-M04-03 | Escaneo → producto encontrado → ficha abierta | E2E |
| TC-M04-04 | Código desconocido → flujo de alta rápida sugerida | E2E |
| TC-M04-05 | Escaneo continuo sostenido sin degradar la UI | Integración |

#### M-05 — Lector QR (Fase 3 · Prioridad: Media)

| ID | Caso crítico | Tipo |
|----|-------------|------|
| TC-M05-01 | Decodificación de QR estándar | Unitaria |
| TC-M05-02 | QR ilegible o ajeno → error manejado sin bloquear el flujo | E2E |
| TC-M05-03 | QR propio resuelve al producto correcto del tenant correcto | E2E |

#### M-06 — Alerta mínimo de productos (Fase 1 · Prioridad: Alta)

| ID | Caso crítico | Tipo |
|----|-------------|------|
| TC-M06-01 | Dispara alerta cuando stock < mínimo; caso borde stock == mínimo documentado y respetado | Unitaria |
| TC-M06-02 | Sin re-disparo en cascada (idempotencia por producto/tenant) | Unitaria |
| TC-M06-03 | Recalcula tras entrada de mercancía y tras venta | Integración |
| TC-M06-04 | Alerta visible en UI sin recarga manual | E2E |
| TC-M06-05 | 200 productos bajo mínimo simultáneos sin colapsar la vista | Integración |

#### M-07 — Reporte de compras (Fase 1 · Prioridad: Alta)

| ID | Caso crítico | Tipo |
|----|-------------|------|
| TC-M07-01 | Sugerido de compra = mínimo − stock, verificado con casos de cálculo fijos aprobados por QA | Unitaria |
| TC-M07-02 | Productos con stock suficiente quedan excluidos | Unitaria |
| TC-M07-03 | El reporte refleja datos en vivo del tenant y SOLO del tenant (aislamiento incluido) | Integración |
| TC-M07-04 | PDF JasperReports correcto: columnas, montos, moneda, paginación | Integración |
| TC-M07-05 | Reporte vacío correcto cuando no hay faltantes | Unitaria |

#### M-08 — CRUD Fiados (Fase 2 · Prioridad: CRÍTICA — dinero del cliente)

| ID | Caso crítico | Tipo |
|----|-------------|------|
| TC-M08-01 | Registro de fiado con precisión decimal exacta (NUMERIC/Decimal; float prohibido) | Unitaria |
| TC-M08-02 | Abono a cuenta reduce saldo; saldo resultante siempre consistente | Unitaria |
| TC-M08-03 | Abono mayor que saldo sigue regla definida (rechazo o ajuste con evidencia) | Unitaria |
| TC-M08-04 | Concurrencia: dos abonos simultáneos al mismo fiado quedan ambos aplicados con suma exacta | Integración |
| TC-M08-05 | Fecha de pago registrada; estado "vencido" calculado correctamente | Unitaria |
| TC-M08-06 | Fiado saldado cierra su estado y no acepta abonos (o aplica regla documentada) | Integración |
| TC-M08-07 | Aislamiento: fiados del tenant A invisibles para B en lista, detalle y exportación | Integración |
| TC-M08-08 | Propiedad (hypothesis): saldo = monto − Σ abonos en 10.000 escenarios aleatorios | Propiedad |
| TC-M08-09 | E2E completo: crear fiado → abonar → saldar → verificar en historial | E2E |

#### M-09 — Historial de fiados (Fase 2 · Prioridad: CRÍTICA — dinero + auditoría legal)

| ID | Caso crítico | Tipo |
|----|-------------|------|
| TC-M09-01 | Cada abono registra fecha, hora y usuario; inmutable (sin UPDATE/DELETE sin bitácora de auditoría) | Integración |
| TC-M09-02 | Propiedad: suma del historial = saldo contable en todo momento | Propiedad |
| TC-M09-03 | Filtros por deudor, fecha y estado devuelven resultados correctos | Integración |
| TC-M09-04 | Exportación del historial completa, legible y aislada por tenant | Integración |
| TC-M09-05 | Durabilidad: un abono confirmado sobrevive el reinicio del contenedor | Integración |

#### M-10 — Scraping BCV (Fase 2 · Prioridad: CRÍTICA — dependencia externa frágil)

| ID | Caso crítico | Tipo |
|----|-------------|------|
| TC-M10-01 | Extrae la tasa correcta desde un fixture HTML del BCV congelado (golden file) | Unitaria |
| TC-M10-02 | HTML modificado/no previsto → fallo RUIDOSO con alerta; nunca una tasa silenciosamente errónea | Unitaria |
| TC-M10-03 | BCV caído o timeout → reintentos con backoff; la última tasa válida se conserva y se marca como obsoleta | Integración |
| TC-M10-04 | Validación de rango: tasa con desviación > 20 % frente a la anterior no se persiste sin confirmación | Unitaria |
| TC-M10-05 | Fin de semana/feriado (el BCV no publica) → comportamiento definido, sin tasa fantasma | Unitaria |
| TC-M10-06 | Frecuencia de peticiones acotada (backoff): sin patrón de abuso hacia el BCV | Integración |

#### M-11 — Actualización dólar BCV (Fase 2 · Prioridad: Alta)

| ID | Caso crítico | Tipo |
|----|-------------|------|
| TC-M11-01 | La actualización manual ejecuta el mismo flujo y las mismas validaciones que la automática | Integración |
| TC-M11-02 | La nueva tasa se propaga a consumidores (precios, reportes) solo tras validación | Integración |
| TC-M11-03 | Un fallo de actualización no corrompe la tasa vigente | Integración |

#### M-12 — Historial tipo de cambio (Fase 2 · Prioridad: Alta)

| ID | Caso crítico | Tipo |
|----|-------------|------|
| TC-M12-01 | Cada captura persiste con timestamp y fuente | Integración |
| TC-M12-02 | Consulta por rango de fechas y visualización correctas | Integración |
| TC-M12-03 | Histórico inmutable: capturas no editables ni borrables | Unitaria |

#### M-13 — Configuración de scraping (Fase 2 · Prioridad: Alta)

| ID | Caso crítico | Tipo |
|----|-------------|------|
| TC-M13-01 | La programación por días/horas ejecuta en el momento exacto (reloj simulado) | Unitaria |
| TC-M13-02 | Múltiples corridas no duplican capturas (idempotencia por fecha/hora) | Unitaria |
| TC-M13-03 | Valores imposibles rechazados en UI (hora 25:00, día inexistente) | Unitaria |
| TC-M13-04 | Configuración aislada por tenant | Integración |

#### M-14 — Promociones WhatsApp (Fase 2 · Prioridad: Alta)

| ID | Caso crítico | Tipo |
|----|-------------|------|
| TC-M14-01 | La plantilla renderiza productos y precios reales del tenant | Integración |
| TC-M14-02 | El precio en Bs usa la tasa BCV vigente al momento del envío | Integración |
| TC-M14-03 | Sin envíos duplicados al mismo destinatario | Integración |
| TC-M14-04 | Opt-out del cliente respetado (cumplimiento) | Integración |
| TC-M14-05 | Errores de la API de Meta: reintento/cola sin pérdida de promociones; métricas visibles | Integración |
| TC-M14-06 | Aislamiento: clientes del tenant B jamás reciben promociones del tenant A | Integración |
| TC-M14-07 | UAT: mensaje legible y correcto en WhatsApp móvil real | UAT |

#### M-15 — Integración balanza (Fase 3 · Prioridad: Alta)

| ID | Caso crítico | Tipo |
|----|-------------|------|
| TC-M15-01 | El parser decodifica tramas RS-232 de referencia (fixtures del análisis de protocolos de Alexis, F3-04) | Unitaria |
| TC-M15-02 | Trama corrupta o ruido se descarta sin colgar el parser ni el stream | Unitaria |
| TC-M15-03 | Desconexión física → reconexión automática sin reiniciar la aplicación | Integración |
| TC-M15-04 | Unidades correctas por protocolo (kg, g, lb) | Unitaria |
| TC-M15-05 | USB y RJ45 cumplen el mismo contrato funcional que RS-232 | Integración |
| TC-M15-06 | Laboratorio: verificación con 2-3 modelos físicos de balanza reales | UAT/Hardware |

### 4.3 Casos transversales

#### TR-01 — Aislamiento multi-tenant (Fase 0+ · CRÍTICA)

| ID | Caso crítico | Tipo |
|----|-------------|------|
| TC-TR01-01 | Todo endpoint de negocio rechaza el recurso de otro tenant (404 preferente; nunca datos ni confirmación de existencia) | Integración (barrido automatizado sobre TODAS las rutas) |
| TC-TR01-02 | Búsqueda, listado y filtros nunca mezclan tenants | Integración |
| TC-TR01-03 | RLS con FORCE (o esquema por tenant): bypass de owner/superusuario bloqueado en la capa de aplicación | Integración |
| TC-TR01-04 | Exportaciones y reportes aislados por tenant | Integración |
| TC-TR01-05 | Los identificadores no permiten inferir la existencia de otros tenants (UUID o equivalente) | Revisión |

#### TR-02 — Autenticación JWT RS256 + tokens dual (Fase 0+ · CRÍTICA)

| ID | Caso crítico | Tipo |
|----|-------------|------|
| TC-TR02-01 | Firma RS256 verificada; rechazo de `alg=none` | Unitaria |
| TC-TR02-02 | Rechazo de sustitución de algoritmo (token HS256 forjado con la clave pública) | Unitaria |
| TC-TR02-03 | Token expirado → 401 con leeway controlado | Unitaria |
| TC-TR02-04 | Token firmado con clave ajena → 401 | Unitaria |
| TC-TR02-05 | Tokens dual: semántica contratante/trabajo documentada y aplicada; el token de trabajo NO accede funciones de administración del contratante | Integración |
| TC-TR02-06 | Matriz de acceso: 401 sin token, 403 con rol insuficiente, en todas las rutas | Integración |
| TC-TR02-07 | Refresh y revocación operan; logout invalida la sesión | Integración |

#### TR-03 — Docker / Zero Trust (Fase 0+ · CRÍTICA)

| ID | Caso crítico | Tipo |
|----|-------------|------|
| TC-TR03-01 | Compose levanta desde clon limpio y queda healthy | Integración/smoke |
| TC-TR03-02 | trivy: 0 CVE críticas en imágenes | CI |
| TC-TR03-03 | gitleaks: 0 secrets en el repositorio | CI |
| TC-TR03-04 | Redes segmentadas; PostgreSQL no expuesto al host | Revisión |
| TC-TR03-05 | Contenedores no-root, límites de recursos, healthchecks, política de reinicio | Revisión |
| TC-TR03-06 | Imágenes con tag o digest fijado (sin `latest`) | Revisión |

#### TR-04 — operational-stream, Go (Fase 3 · Alta)

| ID | Caso crítico | Tipo |
|----|-------------|------|
| TC-TR04-01 | WebSocket autenticado por tenant; mensajes cruzados imposibles | Integración |
| TC-TR04-02 | Reconexión del cliente sin pérdida ni duplicación de eventos | Integración |
| TC-TR04-03 | Backpressure: ráfaga de 1.000 eventos sin pérdida ni agotamiento de memoria | Rendimiento |
| TC-TR04-04 | `go test -race` limpio | CI |

#### TR-05 — Flujos E2E de negocio (Fase 1-2 · Alta)

| ID | Caso crítico | Tipo |
|----|-------------|------|
| TC-TR05-01 | Login → crear producto → ajustar stock → alerta visible | E2E |
| TC-TR05-02 | Login → fiado → abono → saldar → historial correcto | E2E |
| TC-TR05-03 | Reporte de compras descargable con los datos del flujo anterior | E2E |
| TC-TR05-04 | Cambio de tasa → precio actualizado → promoción con precio nuevo | E2E |

---

## 5. Definition of Done por tarea

### 5.1 DoD general — aplica a TODA tarea, toda fase

- [ ] Código en rama `feature/<área>-<ref>`, actualizada contra `main`, sin conflictos.
- [ ] Criterios de aceptación del módulo cumplidos (matriz §4 o `docs/qa/CRITERIOS-ACEPTACION-F0.md`).
- [ ] Suite automatizada nueva o actualizada en verde en CI (umbrales §2.5).
- [ ] Pruebas de aislamiento (TR-01) incluidas si la tarea toca datos de negocio.
- [ ] Sin hallazgos de seguridad abiertos de severidad bloqueante o crítica (trivy, gitleaks, lint de seguridad).
- [ ] Documentación afectada actualizada (si aplica).
- [ ] Informe de tarea emitido con el formato obligatorio (Ref, Descripción, Severidad, Acción sugerida, ¿Bloquea producción?) — todo hallazgo se reporta.
- [ ] Informe de auditoría QA de Emilio emitido → habilita el gate de merge (PLAN-MAESTRO §5: QA ✅ + seguridad ✅ + autorización de Cristian).

### 5.2 DoD específico por rol

| Rol | Definition of Done adicional |
|-----|------------------------------|
| Backend (Nelson) | pytest en verde con cobertura por umbral; migraciones versionadas y reversibles; contrato OpenAPI actualizado; dinero como `NUMERIC`/`Decimal` (fiados); pruebas de concurrencia donde aplique |
| Frontend (Noris) | Vitest en verde; build y lint sin errores; axe sin violaciones críticas; E2E Playwright del flujo afectado; sin secrets en el bundle |
| Go (Victor) | `go test ./... -race` en verde; benchmarks incluidos; contrato de mensajes documentado |
| DevOps (Alfredo) | Compose reproducible desde cero; trivy y gitleaks limpios; healthchecks; logs con rotación; plan de rollback si toca producción |
| UI/UX (Nordanis) | Tokens alineados a la paleta §4 de REQUERIMIENTOS; contraste AA verificado en ambos modos; componentes documentados en `design/` |
| Reportes (Morloy, Javier) | Fórmulas con casos de cálculo verificables aprobados por QA; PDF correcto en contenido y formato |
| Documentación (Carlos) | Enlaces válidos; cada ejemplo ejecutado al menos una vez por el autor |

### 5.3 Gates por fase

| Gate | Criterio de salida de fase (bloquea la siguiente) |
|------|---------------------------------------------------|
| F0 → F1 | CRITERIOS-ACEPTACION-F0.md 100 % en verde; informe QA de F0 emitido y aprobado por Cristian |
| F1 → F2 | Suite F1-09 en verde: CRUDs M-01/02/03, alertas M-06, reporte M-07, arnés TR-01/TR-02 en verde; 0 defectos críticos/altos abiertos |
| F2 → F3 | Suite F2-10 en verde: fiados M-08/09 (incl. propiedad y concurrencia), BCV M-10..13, WhatsApp M-14 sandbox; UAT temprano de fiados con usuario piloto |
| F3 → F4 | Suite F3-06 en verde: lectores M-04/05, balanza M-15 (lab), operational-stream TR-04; 0 defectos críticos abiertos |
| F4 → PROD | Pentest F4-01 y hardening F4-02 aprobados; UAT F4-05 firmado; smoke de producción + rollback F4-06 verificados |

### 5.4 Gestión de defectos

- **Severidades**: Bloqueante (imposible continuar) · Crítica (dinero/datos/seguridad comprometidos) · Alta (función clave degradada) · Media (función secundaria) · Baja (cosmético).
- **Regla de dinero y datos**: todo defecto que afecte montos, saldos o datos entre tenants se reporta como Crítica o superior, sin excepción.
- **Flujo**: hallazgo → issue con formato obligatorio → asignación → corrección → re-test por QA → cierre con evidencia.
- **SLA de re-test (velocidad con rigor)**: Bloqueante/Crítica en ≤ 24 h; Alta ≤ 48 h; Media/Baja en la siguiente ventana de regresión.

---

## 6. Reportes y comunicación

- Informe de auditoría por entregable (formato obligatorio del inversor: Ref, Descripción, Severidad, Acción sugerida, ¿Bloquea producción?) — todo hallazgo se reporta.
- Informe de estado semanal de calidad a Cristian (para el reporte al inversor): cobertura, defectos por severidad, riesgo residual, gates en riesgo.
- Bandera roja inmediata a Cristian si un gate de fase está en riesgo con menos de 5 días hábiles de margen.

---

*Fin del documento. Emilio — QA, Díaz Tech.*
