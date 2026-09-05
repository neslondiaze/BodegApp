# BodegApp — Design System (F0-01)

> Autora: Nordanis (UI/UX, Díaz Tech) · Reporta a: Cristian (Project Director) · Fecha: 03/09/2026
> Fuente de verdad de color y tipografía: `docs/REQUERIMIENTOS.md` §4 (paleta definida por el inversor, 01/09/2026).
> Estilo base: Flat Design (validado con ui-ux-pro-max para dashboards densos). Sin degradados ni sombras complejas.
> Modelo de referencia del inversor (`design/referencias/modelo-referencia.png`): analizado en §9.

## 0. Principios

1. **Paleta cerrada**: los hex de marca provienen EXCLUSIVAMENTE de REQUERIMIENTOS.md §4. No se inventan colores nuevos. Los únicos valores derivados (superficie clara, bordes, sombras, estados hover/disabled) se generan por transformación algorítmica documentada de los hex oficiales (mezcla de opacidad con negro/blanco) y se declaran como tales en cada tabla.
2. **Modo claro y oscuro de primera clase**: cada token tiene valor para ambos temas; el cambio se realiza con el atributo `data-theme` en `<html>`.
3. **Densidad dashboard**: la operatoria de bodega exige información visible por pantalla. Tipografía base 14px, filas de tabla compactas con target táctil mínimo 44px.
4. **Accesibilidad no negociable**: toda combinación texto/fondo documentada con ratio WCAG 2.1. Las combinaciones que fallan AA quedan PROHIBIDAS por regla (ver §7).
5. **Números tabulares**: precios, cantidades, montos de fiados y tasas BCV usan `font-feature-settings: "tnum"` para alineación de columnas.

## 1. Tokens de color

### 1.1 Semántica de roles

| Rol | Uso en BodegApp |
|-----|-----------------|
| `primary` | CTA principal, logo, navegación activa, acciones destructivas de confirmación (en claro comparte familia con error) |
| `primary-deep` | Vinotinto: hover del primario, marca, botón destructivo en claro (distinción semántica) |
| `secondary` | Amarillo oro: ofertas, badges de stock bajo, promociones |
| `accent` | Verde: stock disponible, éxito de pago/abono, confirmaciones |
| `surface` | Fondo de tarjetas, tablas, modales, inputs |
| `background` | Lienzo de la aplicación |
| `text-primary` / `text-secondary` | Jerarquía de texto |
| `border` | Separadores, bordes de inputs/cards/tablas |
| `on-primary` / `on-secondary` / `on-accent` | Color de texto legible sobre cada color de marca (fijado por accesibilidad, ver §7) |

### 1.2 Modo claro (hex oficiales §4)

| Token | Hex | Origen |
|-------|-----|--------|
| `--color-primary` | `#C41230` | Oficial §4 (Rojo Vitalidad) |
| `--color-primary-deep` | `#800020` | Oficial §4 (Vinotinto) |
| `--color-secondary` | `#FFB81C` | Oficial §4 (Amarillo Oro) |
| `--color-accent` | `#2E7D32` | Oficial §4 (Verde Frescura) |
| `--color-background` | `#F8F9FA` | Oficial §4 (Blanco grisáceo) |
| `--color-surface` | `#FFFFFF` | Derivado documentado (§4 no define tarjeta en claro; blanco puro jerarquiza sobre fondo grisáceo) |
| `--color-text-primary` | `#212529` | Oficial §4 (Gris casi negro) |
| `--color-text-secondary` | `#6C757D` | Oficial §4 (Gris medio) |
| `--color-border` | `color-mix(in srgb, #6C757D 25%, transparent)` | Derivado algorítmico del oficial `#6C757D` (§4 no define borde en claro) |
| `--color-on-primary` | `#FFFFFF` | Derivado: blanco sobre `#C41230` = 6.04:1 AA |
| `--color-on-primary-deep` | `#FFFFFF` | Derivado: blanco sobre `#800020` = 10.83:1 AA |
| `--color-on-secondary` | `#212529` | Derivado OBLIGATORIO: `#212529` sobre `#FFB81C` = 8.91:1. El blanco sobre amarillo queda PROHIBIDO (1.73:1, ver §7) |
| `--color-on-accent` | `#FFFFFF` | Derivado: blanco sobre `#2E7D32` = 5.13:1 AA |
| `--color-destructive` | `#800020` | Reutiliza el oficial Vinotinto para distinguir "eliminar" del CTA primario |
| `--color-on-destructive` | `#FFFFFF` | 10.83:1 AA |

### 1.3 Modo oscuro (hex oficiales §4)

| Token | Hex | Origen |
|-------|-----|--------|
| `--color-primary` | `#E53935` | Oficial §4 (Rojo suave) |
| `--color-primary-deep` | `#C41230` | Oficial §4 (variante para hover en oscuro: al aclarar no se degrada el contraste) |
| `--color-secondary` | `#FFCA28` | Oficial §4 (Amarillo ámbar) |
| `--color-accent` | `#81C784` | Oficial §4 (Verde esmeralda claro) |
| `--color-background` | `#121212` | Oficial §4 (Gris casi negro) |
| `--color-surface` | `#1E1E1E` | Oficial §4 (Gis elevado, tarjetas/contenedores) |
| `--color-surface-raised` | `color-mix(in srgb, #FFFFFF 6%, #1E1E1E)` | Derivado algorítmico del oficial `#1E1E1E` (tercer nivel de elevación: modales, dropdowns) |
| `--color-text-primary` | `#FFFFFF` | Oficial §4 |
| `--color-text-primary-soft` | `#E0E0E0` | Oficial §4 (variante listada por el inversor) |
| `--color-text-secondary` | `#9E9E9E` | Oficial §4 (Gris medio) |
| `--color-border` | `#2C2C2C` | Oficial §4 (Gris sutil, bordes/separadores) |
| `--color-on-primary` | `#FFFFFF` | 4.23:1 — AA large/UI (regla de uso en §7) |
| `--color-on-secondary` | `#121212` | 12.25:1 AA. Blanco sobre ámbar PROHIBIDO |
| `--color-on-accent` | `#121212` | 9.31:1 AA. Blanco sobre esmeralda PROHIBIDO (2.01:1) |
| `--color-destructive` | `#E53935` | Oficial §4 (único rojo del modo oscuro) |
| `--color-on-destructive` | `#FFFFFF` | 4.23:1 — AA large/UI |

### 1.4 Estados de color (transformaciones algorítmicas — no hex nuevos)

Los estados hover/focus/disabled se generan mezclando el token base con negro (claro) o blanco (oscuro), o reduciendo opacidad. Nunca introducen un hex de paleta ajeno a §4.

| Estado | Modo claro | Modo oscuro |
|--------|------------|-------------|
| Hover (primary) | `color-mix(in srgb, #C41230 92%, #000)` → uso de `primary-deep #800020` como alternativa de marca | `color-mix(in srgb, #E53935 90%, #FFF)` |
| Hover (superficie) | `color-mix(in srgb, #000 4%, #FFFFFF)` | `color-mix(in srgb, #FFF 6%, #1E1E1E)` |
| Focus ring | `--color-primary` a 2px con offset 2px | `--color-primary` a 2px con offset 2px |
| Disabled | Token base al 40% de opacidad + `cursor: not-allowed` | Idéntico |
| Overlay modal | `rgba(0,0,0,0.5)` | `rgba(0,0,0,0.7)` |

## 2. Tipografía

Fuentes oficiales §4: **Plus Jakarta Sans** para headlines (títulos, categorías, nombres de tiendas) e **Inter** para body/UI (textos, precios, botones). Fallbacks: Cabinet Grotesk (PJS) y SF Pro Display / system-ui (Inter), según §4.

Pesos empleados: PJS 600/700/800 · Inter 400/500/600/700.

### 2.1 Escala tipográfica

| Token | Fuente | Peso | Tamaño | Line-height | Letter-spacing | Uso |
|-------|--------|------|--------|-------------|----------------|-----|
| `--font-h1` | Plus Jakarta Sans | 800 | 32px | 1.2 | -0.02em | Título de página (Dashboard, "Productos") |
| `--font-h2` | Plus Jakarta Sans | 700 | 24px | 1.25 | -0.01em | Título de sección, título de modal |
| `--font-h3` | Plus Jakarta Sans | 700 | 20px | 1.3 | -0.01em | Título de card, nombre de tienda |
| `--font-h4` | Plus Jakarta Sans | 600 | 18px | 1.35 | 0 | Subtítulos, encabezados de grupo |
| `--font-body-lg` | Inter | 400 | 16px | 1.5 | 0 | Texto de lectura, helper text |
| `--font-body` | Inter | 400 | 14px | 1.5 | 0 | Texto por defecto (dashboard denso) |
| `--font-body-sm` | Inter | 400 | 13px | 1.45 | 0 | Metadatos, celdas secundarias |
| `--font-caption` | Inter | 400 | 12px | 1.4 | 0.01em | Labels de campos, badges, timestamps |
| `--font-price` | Inter | 600 | 20px | 1.2 | 0 | Precio de producto (`tnum`) |
| `--font-data` | Inter | 500 | 14px | 1.4 | 0 | Celdas numéricas de tablas, montos de fiados, tasa BCV (`tnum`) |
| `--font-button` | Inter | 600 | 14px | 1 | 0.02em | Etiqueta de botón |
| `--font-overline` | Plus Jakarta Sans | 700 | 12px | 1.2 | 0.08em | Overline de card, categoría en mayúsculas |

Reglas:
- Título de página siempre `h1` único por vista.
- Precios y montos SIEMPRE con `font-variant-numeric: tabular-nums`.
- Texto de body nunca por debajo de 12px (mínimo accesible); `caption` solo para labels no críticos.

## 3. Espaciado, radios y elevación

### 3.1 Espaciado (base 4px)

| Token | Valor |
|--------|-------|
| `--space-0` | 0 |
| `--space-1` | 4px |
| `--space-2` | 8px |
| `--space-3` | 12px |
| `--space-4` | 16px |
| `--space-5` | 20px |
| `--space-6` | 24px |
| `--space-8` | 32px |
| `--space-10` | 40px |
| `--space-12` | 48px |
| `--space-16` | 64px |

Uso canónico: padding de card 16px (`--space-4`), gap de grid 24px (`--space-6`), separación de secciones 32px (`--space-8`), margen de página 24px (`--space-6`).

### 3.2 Radios

| Token | Valor | Uso |
|--------|-------|-----|
| `--radius-sm` | 4px | Badges, chips, tags |
| `--radius-md` | 8px | Botones, inputs, selects, tabs |
| `--radius-lg` | 12px | Cards, tablas |
| `--radius-xl` | 16px | Modales, drawers |
| `--radius-full` | 9999px | Avatares, pills de estado, toggles |

### 3.3 Sombras y elevación (Flat Design: sutiles, dos niveles)

| Token | Modo claro | Modo oscuro |
|--------|-------------|-------------|
| `--shadow-1` (cards, inputs) | `0 1px 2px rgba(0,0,0,0.08)` | Sin sombra: borde `--color-border` 1px sobre `--color-surface` |
| `--shadow-2` (modales, dropdowns) | `0 4px 16px rgba(0,0,0,0.12)` | Sin sombra: borde 1px + `--color-surface-raised` |
| `--shadow-focus` | Ver estados (§1.4) | Ver estados (§1.4) |

En modo oscuro la elevación se comunica con superficie más clara + borde, no con sombra (convención Material oscuro, consistente con §4 que define tarjetas por color y no por sombra).

## 4. Estados interactivos

| Estado | Superficie | Botón primario | Input | Tabla |
|--------|-----------|----------------|-------|-------|
| Default | `--color-surface` | `--color-primary` | borde `--color-border` 1px | fila transparente |
| Hover | mezcla 4% negro (claro) / 6% blanco (oscuro) | mezcla 8% hacia oscuro del tema | borde `--color-text-secondary` | fila con fondo hover de superficie |
| Focus visible | — | `outline: 2px solid --color-primary; outline-offset: 2px` | `outline: 2px solid --color-primary; outline-offset: 2px` + borde a primario | celda navegable con el mismo outline |
| Disabled | — | opacidad 40%, `cursor: not-allowed`, sin hover | opacidad 40% | texto a `--color-text-secondary` |
| Loading | — | spinner 16px + texto, `aria-busy="true"` | spinner inline a la derecha | skeleton con mezcla 8% |

Regla de motion: transiciones 150-200ms `ease-out`; se respeta `prefers-reduced-motion: reduce` (sin transición). Nada anima `width/height`.

## 5. Especificación de componentes

### 5.1 Botones

Variantes: **primario** (fondo primario, texto `on-primary`), **secundario** (borde 1px `--color-border`, texto `--color-text-primary`, fondo `--color-surface`), **ghost** (transparente, texto `--color-primary` claro / `--color-text-primary` oscuro, hover con fondo de superficie), **destructivo** (fondo `--color-destructive`, texto `on-destructive`).

| Tamaño | Alto | Padding H | Fuente |
|--------|------|-----------|--------|
| `sm` | 32px | 12px | `--font-caption` peso 600 |
| `md` | 40px | 16px | `--font-button` |
| `lg` | 48px | 24px | `--font-button` 16px |

Reglas: ancho mínimo de target táctil 44px en móvil (usar `lg`); icono opcional 16px a la izquierda con gap 8px (SVG de Lucide/Heroicons, nunca emoji); botón destructivo requiere confirmación (modal §5.7); estados según §4.

### 5.2 Inputs

Alto 40px, radio `--radius-md`, borde 1px `--color-border`, fondo `--color-surface` (en claro, blanco), label visible arriba (`--font-caption`, `--color-text-primary`) — PROHIBIDO placeholder como único label. Helper text debajo con `--color-text-secondary`; error con texto del rol destructivo + icono 16px, mensaje a 4px bajo el campo. Focus según §4. Inputs de monto/precio con `tnum` y alineación derecha.

### 5.3 Cards de producto

Estructura: imagen cuadrada 96px (radio `--radius-md`) o placeholder con inicial del producto en PJS 700 sobre fondo hover de superficie; nombre en `--font-h3`; categoría en `--font-overline` con `--color-text-secondary`; precio en `--font-price` con `--color-text-primary`; badge de stock (§5.5); CTA primario `sm` o icon-button de editar. Padding `--space-4`, radio `--radius-lg`, sombra `--shadow-1`. Estados: hover eleva fondo (§1.4); el CTA completo de la card es accesible por teclado con `focus-visible`.

### 5.4 Tablas de inventario

Encabezado: fondo hover de superficie, texto `--font-caption` peso 600 `--color-text-primary`, alto 40px. Filas: alto 48px (44px mínimo táctil), borde inferior 1px `--color-border`, texto `--font-data` para números. Columnas canónicas de inventario: Producto · Código de barras (M-04) · Stock · Mínimo · Precio Bs · Precio USD (tasa BCV) · Estado · Acciones. Filas con stock bajo/agotado llevan badge (§5.5) además de color — nunca solo color. Ordenación por columna con indicador textual (asc/desc). Vacío: mensaje centrado + CTA de alta.

### 5.5 Badges de stock

| Estado | Claro | Oscuro | Texto |
|--------|-------|--------|-------|
| Disponible (stock ≥ mínimo) | fondo `#2E7D32` | fondo `#81C784` | claro: `#FFFFFF` (5.13) · oscuro: `#121212` (9.31) |
| Bajo (stock < mínimo, M-06) | fondo `#FFB81C` | fondo `#FFCA28` | claro: `#212529` (8.91) · oscuro: `#121212` (12.25) |
| Agotado (stock = 0) | fondo `#C41230` | fondo `#E53935` | claro: `#FFFFFF` (6.04) · oscuro: `#FFFFFF` solo large/UI (4.23) — ver §7 |

Fuente `--font-caption` peso 600, radio `--radius-sm`, padding 4px 8px, ícono de punto 6px a la izquierda. En modo oscuro el badge "agotado" en texto pequeño usa variante outline: borde 1px `#E53935` + texto `#FFCA28`/`#FFFFFF` sobre fondo transparente (contraste textual garantizado).

### 5.6 Alertas

| Tipo | Fondo | Borde izquierdo | Icono/texto |
|------|-------|-----------------|-------------|
| Éxito (pago/abono registrado) | mezcla 8% de accent sobre superficie | 4px `--color-accent` | icono check + texto `--color-text-primary`; título `--font-h4` |
| Advertencia (stock bajo, revisar mínimos) | mezcla 12% de secondary sobre superficie | 4px `--color-secondary` | cuerpo y título: `--color-text-primary` sobre el fondo mezcla (claro: `#212529` sobre `#FFF6E4` = 14.36, §7.1; oscuro: `#FFFFFF` sobre `#39331F` = 12.60, §7.2); icono de alerta: chip de fondo `--color-secondary` sólido con texto `#212529`/`#121212` (8.91/12.25) |
| Error (fallo de scraping BCV, validación) | mezcla 8% de destructive sobre superficie | 4px `--color-destructive` | texto `--color-text-primary` |
| Info (tasa actualizada) | fondo hover de superficie | 4px `--color-border` | texto `--color-text-primary` (claro: `#212529` sobre `#F5F5F5` = 14.15, §7.1 — remedición O-N-001) |

Cierre opcional con icon-button 24px `aria-label="Cerrar alerta"`. Alertas de stock bajo son-dismissible solo manualmente (operatoria M-06).

Remedición QA F0-01 OBS-03 (modo oscuro): el cuerpo y título de la alerta usan `--color-text-primary` (`#FFFFFF` = 12.60:1 sobre la mezcla 12% de ámbar, §7.2). El fondo ámbar sólido queda reservado EXCLUSIVAMENTE al chip de icono/título con texto oscuro (`#121212` sobre `#FFCA28` = 12.25:1). PROHIBIDO `#121212` directo sobre la mezcla ámbar (1.49:1, ilegible — ver §7.2).

### 5.7 Modales

Overlay según §1.4; superficie `--color-surface` (oscuro: `--color-surface-raised`), radio `--radius-xl`, ancho máx 560px, padding `--space-6`; título `--font-h2` + botón de cierre 24px; foco atrapado dentro (focus trap), cierre con `Escape`, retorno de foco al disparador. Uso principal: confirmaciones destructivas, alta/edición de producto, registro de abono a fiado.

### 5.8 Sidebar / Topbar

**Sidebar** (≥1024px): fondo `--color-surface`, ancho 240px, item de navegación 44px de alto con icono 20px + label `--font-body` peso 500; item activo: fondo mezcla 8% de primario + texto `--color-primary` + barra 3px primaria a la izquierda; en oscuro, item activo con texto `#FFFFFF` (barra primaria como identificador). Secciones: Panel · Productos · Proveedores · Fiados · Tipo de cambio · Promociones · Configuración.
**Topbar** (siempre visible): fondo `--color-surface`, borde inferior 1px `--color-border`, alto 56px; contiene: nombre de tienda (`--font-h4` PJS), indicador de tasa BCV actual (`--font-data`, refresca con M-11), selector de tema claro/oscuro, menú de cuenta. En <1024px el sidebar colapsa a drawer con overlay (§5.7).

## 6. Iconografía y breakdowns

- Iconos: SVG outline de **Lucide** o **Heroicons**, trazo 1.5-2px, 16/20/24px. PROHIBIDO emoji como icono.
- Breakpoints (mobile-first): 375 · 768 · 1024 · 1440 px.
- `viewport` sin `maximum-scale` (no se bloquea el zoom).

## 7. Accesibilidad — Contraste WCAG 2.1 AA documentado

Cálculos reales (fórmula WCAG 2.1). Umbral texto normal 4.5:1; texto grande (≥24px regular o ≥18.66px bold) y componentes UI 3:1.

### 7.1 Modo claro

| Combinación | Ratio | Texto normal AA | Texto grande / UI AA | Veredicto |
|-------------|-------|-----------------|----------------------|-----------|
| `#212529` sobre `#F8F9FA` | 14.63 | PASS | PASS | Autorizado general |
| `#212529` sobre `#FFFFFF` | 15.43 | PASS | PASS | Autorizado general |
| `#6C757D` sobre `#FFFFFF` | 4.69 | PASS | PASS | Autorizado en superficies |
| `#6C757D` sobre `#F8F9FA` | 4.45 | **FAIL (0.05)** | PASS | Solo texto grande ≥18.66px bold o ≥24px; para texto pequeño usar sobre `#FFFFFF` |
| `#C41230` sobre `#F8F9FA` | 5.73 | PASS | PASS | Autorizado (links, texto de marca) |
| `#C41230` sobre `#FFFFFF` | 6.04 | PASS | PASS | Autorizado |
| `#800020` sobre `#F8F9FA` | 10.28 | PASS | PASS | Autorizado |
| `#FFFFFF` sobre `#C41230` | 6.04 | PASS | PASS | Botón primario |
| `#FFFFFF` sobre `#800020` | 10.83 | PASS | PASS | Botón destructivo |
| `#212529` sobre `#FFB81C` | 8.91 | PASS | PASS | ÚNICO texto autorizado sobre amarillo |
| `#FFFFFF` sobre `#FFB81C` | 1.73 | **FAIL** | **FAIL** | **PROHIBIDO** |
| `#C41230` sobre `#FFB81C` | 3.49 | FAIL | PASS | Solo texto grande/UI sobre amarillo |
| `#FFFFFF` sobre `#2E7D32` | 5.13 | PASS | PASS | Badge disponible |
| `#2E7D32` sobre `#F8F9FA` | 4.86 | PASS | PASS | Texto de éxito sobre fondo |
| `#2E7D32` sobre `#FFFFFF` | 5.13 | PASS | PASS | Autorizado |
| `#212529` sobre `#FFF6E4` (mezcla 12% `#FFB81C` sobre `#FFFFFF`) | 14.36 | PASS | PASS | Alerta "Advertencia" claro: cuerpo/título sobre fondo mezcla (remedición QA F0-01 OBS-03) |
| `#212529` sobre `#F5F5F5` (hover de superficie: mezcla 4% `#000` sobre `#FFFFFF`) | 14.15 | PASS | PASS | Alerta "Info" claro: cuerpo sobre fondo hover (remedición O-N-001) |
| `#212529` sobre `#F5F5F5` (hover de superficie: mezcla 4% `#000` sobre `#FFFFFF`) | 14.15 | PASS | PASS | Encabezado de tabla §5.4 claro: texto `--font-caption` peso 600 12px con `--color-text-primary` (Remediación QA F0-01 OBS-04; `#6C757D` previo = 4.30 FAIL AA) |

### 7.2 Modo oscuro

| Combinación | Ratio | Texto normal AA | Texto grande / UI AA | Veredicto |
|-------------|-------|-----------------|----------------------|-----------|
| `#FFFFFF` sobre `#121212` | 18.73 | PASS | PASS | Autorizado general |
| `#E0E0E0` sobre `#121212` | 14.19 | PASS | PASS | Autorizado general |
| `#E0E0E0` sobre `#1E1E1E` | 12.63 | PASS | PASS | Autorizado general |
| `#9E9E9E` sobre `#121212` | 6.99 | PASS | PASS | Autorizado |
| `#9E9E9E` sobre `#1E1E1E` | 6.22 | PASS | PASS | Autorizado |
| `#E53935` sobre `#121212` | 4.43 | **FAIL (0.07)** | PASS | Rojo solo como texto grande/UI; texto pequeño usar `#FFCA28` o `#FFFFFF` |
| `#E53935` sobre `#1E1E1E` | 3.94 | FAIL | PASS | Solo componentes UI y texto grande |
| `#FFFFFF` sobre `#E53935` | 4.23 | **FAIL (0.27)** | PASS | Botón primario oscuro: etiqueta ≥16px/600 se considera texto grande; ver §7.3 regla 4 y Anexo (badge agotado outline) |
| `#121212` sobre `#E53935` | 4.43 | FAIL (0.07) | PASS | Alternativa al anterior, mismo veredicto |
| `#FFCA28` sobre `#121212` | 12.25 | PASS | PASS | Autorizado (ofertas, stock bajo) |
| `#121212` sobre `#FFCA28` | 12.25 | PASS | PASS | ÚNICO texto sobre ámbar |
| `#FFFFFF` sobre `#39331F` (mezcla 12% `#FFCA28` sobre `#1E1E1E`) | 12.60 | PASS | PASS | Alerta "Advertencia" oscuro: cuerpo/título sobre fondo mezcla (remedición QA F0-01 OBS-03) |
| `#121212` sobre `#39331F` | 1.49 | **FAIL** | **FAIL** | **PROHIBIDO** — defecto original de la OBS-03; el texto oscuro solo va sobre el chip ámbar sólido |
| `#FFFFFF` sobre `#2C2C2C` (hover de superficie oscuro: mezcla 6% `#FFF` sobre `#1E1E1E`) | 13.97 | PASS | PASS | Encabezado de tabla §5.4 oscuro: texto con `--color-text-primary` (Remediación QA F0-01 OBS-04). Verificación del secundario previo: `#9E9E9E` sobre `#2C2C2C` = 5.21 PASS AA — el defecto 4.30 era exclusivo del modo claro |
| `#81C784` sobre `#121212` | 9.31 | PASS | PASS | Autorizado |
| `#81C784` sobre `#1E1E1E` | 8.28 | PASS | PASS | Autorizado |
| `#121212` sobre `#81C784` | 9.31 | PASS | PASS | ÚNICO texto sobre esmeralda |
| `#FFFFFF` sobre `#81C784` | 2.01 | **FAIL** | **FAIL** | **PROHIBIDO** |

### 7.3 Reglas de accesibilidad derivadas

1. Sobre amarillo (`#FFB81C`/`#FFCA28`) el texto es SIEMPRE oscuro (`#212529`/`#121212`). Blanco sobre amarillo: prohibido.
2. Sobre verde esmeralda `#81C784` el texto es SIEMPRE `#121212`. Blanco sobre esmeralda: prohibido.
3. Texto secundario claro `#6C757D` en texto pequeño solo sobre `#FFFFFF`; sobre `#F8F9FA` requerir tamaño grande.
4. En modo oscuro, el rojo `#E53935` no se usa como texto pequeño sobre fondo; como CTA grande o componente UI está autorizado.
5. Focus visible obligatorio (outline 2px con offset), navegación completa por teclado, `aria-label` en icon-buttons, estados de stock comunicados con texto+icono además de color.

## 8. Gobernanza de tokens

- Fuente de verdad de implementación: `design/tokens/tokens.css` (CSS custom properties) y `design/tokens/tokens.json` (formato Tailwind para Noris, F0-05).
- Prohibido hex crudo en componentes: siempre `var(--color-*)` o clases Tailwind generadas desde `tokens.json`.
- Cambios a esta especificación requieren aprobación de Cristian; cambios de paleta requieren aprobación del inversor.

## 9. Análisis del modelo de referencia

> Material: `design/referencias/modelo-referencia.png` (795×570 px, PNG RGBA) — captura adjuntada por el inversor en el ODT (integridad byte-idéntica verificada por QA F0-01). Muestra **"FácilVirtual"**, un POS de escritorio tipo Windows Forms (.NET) con estética Windows XP/7, en sesión "Caja 01 · Cajero: Administrador".
> Método del análisis: descripción estructurada provista por el inversor (levantamiento asistido por IA de la captura), contrastada con verificación cromática independiente por muestreo de píxeles del PNG — los colores dominantes coinciden con las zonas descritas: bloque de totales negro `#000000`, verdes de sistema `#3E8525`/`#439D21`, chrome gris Windows `#E8EDE9`, botonera `#22242A`. Los hex del legacy NO se incorporan a la paleta (regla §0.1).

### 9.1 Inventario de la referencia — qué muestra

> Descripción completa de la referencia: [referencias/modelo-referencia.md](./referencias/modelo-referencia.md) (descripción AI del inversor, fuente primaria de este análisis).

| Zona | Elementos relevados |
|------|---------------------|
| A · Entrada de productos (superior izquierdo) | TextBox "Código de barras" (enfocado, vacío) · NumericUpDown "Cantidad" (valor 1) · botón "Buscar artículo" con icono de lupa. Grilla DataGridView de 6 columnas: `#`, Código (EAN-13 o internos como `DEPT003`), Descripción (ej. "LECHE ENTERA SANCOR C/HIERRO"), Cantidad, Unitario, Importe. Botones de fila: Quitar · Descuento · Recargo · Cambiar cantidad · Cambiar precio |
| B · Facturación y cliente (inferior izquierdo) | "Datos del comprobante": Fecha (18/04/2014), Tipo ("Ticket Fiscal"), Nro., Observaciones. "Datos del cliente": Sr/a. ("- Cliente Ocasional -"), Domicilio, Localidad, Teléfonos, Condición IVA ("Consumidor Final"), botón "Cambiar cliente" |
| C · Totales y accesos (lateral derecho) | Bloque de totales negro: Subtotal (verde regular), Descuento/Recargo (blanco), Total (verde brillante, máxima jerarquía). CTA verde grande "F2 - Cobrar" · secundarios "F4 - Nueva venta", "F5 - Ver precio". Botonera de categorías 2×4: Almacén · Panadería · Fiambrería · Verduras y Frutas · Carnicería · Varios · Departamento 04 · Departamento 08 |
| D · Pie de pantalla | Banner de logo del proveedor (inferior derecho) · barra de estado verde "Caja 01 · Cajero: Administrador" (inferior izquierdo) |

Contrastes informativos medidos en la captura (no normativos para BodegApp): blanco sobre bloque negro 21.00:1 · Total `#439D21` sobre negro 6.08:1 · Subtotal `#3E8525` sobre negro 4.59:1 · blanco sobre cabecera verde 4.58:1 · blanco sobre botonera 15.51:1. El legacy alcanza valores AA de forma puntual y no sistemática; BodegApp garantiza AA por matriz calculada (§7).

### 9.2 Elementos CONSERVADOS/ADAPTADOS — y por qué

| Elemento legacy | Decisión | Destino BodegApp | Justificación |
|-----------------|----------|------------------|---------------|
| Campo "Código de barras" + "Buscar artículo" | CONSERVAR (adaptar) | M-04: input de escaneo con foco automático + modal de escaneo; búsqueda por descripción como fallback | Identificar por código ES la operación central de bodega. En web se suman lector USB (se comporta como teclado) y cámara del teléfono |
| Grilla de ventas (6 columnas) | ADAPTAR | §5.4 tablas de inventario M-02: Producto · Código de barras · Stock · Mínimo · Precio Bs · Precio USD · Estado · Acciones | Se conserva el patrón informativo índice/código/descripción/cantidad/precio/importe. BodegApp agrega Stock, Mínimo y Estado porque es sistema de inventario, no solo caja |
| Botones de fila (Quitar, Descuento, Recargo, Cambiar cantidad, Cambiar precio) | ADAPTAR | Menú de acciones por fila en M-02 y en el flujo de venta; "Quitar" exige confirmación destructiva (§5.7) | Descuento y recargo son operatoria real del comercio venezolano; en web se agrupan en menú de fila para no saturar la tabla (densidad §0.3) |
| Datos del cliente + "Cambiar cliente" | ADAPTAR | M-08/M-09: cliente asociado a fiado con abono y fecha de pago; selector de cliente en el checkout | El fiado es operación central del negocio (REQUERIMIENTOS §5); "- Cliente Ocasional -" se conserva como default de venta de contado |
| Bloque de totales con Total de máxima jerarquía | CONSERVAR (re-estilizar) | Panel de resumen del checkout: Subtotal/Descuento/Total con `--font-price`/`--font-data` y `tnum` | La jerarquía numérica del legacy es correcta para cobrar; se reconstruye con tokens BodegApp (fondo `--color-surface`, montos en `--color-text-primary`) |
| CTA dominante "F2 - Cobrar" | ADAPTAR | Botón primario `lg` (48px, §5.1) del checkout | Se conserva el patrón de acción única dominante; el color pasa a `--color-primary` (rojo de marca), no al verde del legacy |
| "F4 - Nueva venta" / "F5 - Ver precio" | ADAPTAR | Botones secundarios + atajos de teclado web equivalentes | Eficiencia del cajero experto; los atajos son capa adicional, NUNCA única vía (accesibilidad §7.3 regla 5) |
| Botonera de categorías 2×4 | ADAPTAR | Chips de filtrado por categoría en M-02 + overline de categoría en card de producto (§5.3) | La navegación rápida por categoría se conserva; en web son chips scrollables (375px móvil) y las categorías son datos del tenant, no botones fijos |
| Barra de estado "Caja 01 · Cajero: Administrador" | CONSERVAR (reubicar) | Topbar §5.8: tienda activa + usuario + tasa BCV en vivo (M-10/M-11) + selector de tema | Contexto de sesión siempre visible; en multi-tenant identifica la tienda del tenant (M-01) |

### 9.3 Elementos DESCARTADOS — y por qué

| Elemento legacy | Decisión | Justificación |
|-----------------|----------|---------------|
| Estética Windows Forms XP/7: chrome gris `#E8EDE9`, bordes 3D, NumericUpDown, DateTimePicker, ComboBox nativos | DESCARTAR | La identidad obligatoria es el design system BodegApp (REQUERIMIENTOS §4; §1-§3 de este documento). Los controles nativos de escritorio no existen en web; sus equivalentes (date picker, select, stepper) se estilizan con tokens |
| Verdes de sistema `#3E8525`/`#439D21` (cabeceras de grilla, barra de estado, "verde dinero" del Total) | DESCARTAR | Paleta cerrada (§0.1): el único verde es `#2E7D32`/`#81C784` con rol accent (stock disponible, éxito). La función del "verde dinero" se resuelve con jerarquía tipográfica y `tnum`, sin hex nuevos |
| Botonera gris `#22242A` de botones planos sin jerarquía | DESCARTAR | BodegApp exige jerarquía de acciones (§5.1: primario/secundario/ghost/destructivo); el legacy no distingue CTA de acción secundaria |
| Banner de logo del proveedor al pie | DESCARTAR | La marca vive en topbar/sidebar (§5.8); el pie web es espacio de contenido y el mobile-first 375px no admite banners decorativos |
| "Datos del comprobante": Tipo "Ticket Fiscal", Nro., fecha por defecto vencida (2014) | DESCARTAR en F0 | REQUERIMIENTOS §3 no define facturación ni impresión fiscal: el checkout BodegApp registra venta/fiado (M-08) sin comprobante. Reevaluable si el inversor amplía alcance (anotado para backlog) |
| Botones "Departamento 04/08" sin etiquetar | DESCARTAR | Son placeholders sin datos: en BodegApp las categorías las define cada tenant (M-01); no existen botones hardcodeados |

### 9.4 Mejoras WEB aplicadas — mapeo POS de escritorio legacy → BodegApp web moderno

| Aspecto del legacy | Mejora BodegApp | Ref. |
|--------------------|----------------|------|
| Aplicación de escritorio a resolución fija | Web responsive mobile-first: 375 → 768 → 1024 → 1440 px | §6 |
| Atajos F2/F4/F5 como vía principal del operador | Teclado + táctil + cámara escáner; botones siempre visibles, atajos como capa extra | §4, §7.3 regla 5 |
| TextBox enfocado sin indicador accesible | Focus ring 2px con offset 2px en todos los interactivos; navegación completa por teclado | §4 |
| Grilla blanca con cabecera verde saturada | Tabla tokenizada: cabecera sobria, filas 48px (target 44px), estado con badge texto+icono (nunca solo color), vacío con CTA de alta | §5.4, §5.5 |
| Botonera fija 2×4 y paneles apilados | Sidebar ≥1024px / drawer en móvil, chips de categoría, dashboard denso (14px, tablas compactas) | §5.8, §0.3 |
| Contraste casual (AA por coincidencia, sin sistema) | Matriz de contraste AA calculada con prohibiciones explícitas, en modo claro Y oscuro | §7 |
| Montos con coma decimal y alineación no garantizada | `tabular-nums` obligatorio en precios, montos de fiados y tasas BCV (Bs y USD) | §2.1 |
| Barra de estado rígida inferior | Topbar con tienda, tasa BCV en vivo (M-10/M-11), selector de tema y cuenta | §5.8 |
| "Cantidad" con NumericUpDown físico | Stepper con target táctil 44px, label visible, validación con helper/error text | §5.2 |
| Monopuesto (una caja, un rol) | Multi-tenant: tienda por tenant (M-01), sesión y rol de usuario en topbar | REQUERIMIENTOS §2, §5.8 |

Síntesis del mapeo: la referencia valida la **operatoria** de bodega (escanear, listar, cobrar, fiar, categorizar, contextualizar la sesión) y **no la estética**. BodegApp conserva el *qué* y reemplaza el *cómo* con el design system de §1-§7.

---

## 10. Ticket Fiscal (M-16)

> Sección añadida por F0-09 (Nordanis, UI/UX — 05/09/2026). Requerimiento: `docs/REQUERIMIENTOS.md` M-16 (línea 39, decisión del inversor 04/09/2026, resuelve O-N-005). Delegación y estándar: `docs/plantillas/RECORDATORIO-ARRANQUE-NORDANIS.md`.
> **El ticket fiscal es un documento legal-fiscal**: legibilidad y cumplimiento de campos obligatorios VE tienen prioridad ABSOLUTA sobre estética (§10.1 principio 1). El ticket físico es monocromático (negro sobre papel térmico): la paleta de color §1 aplica solo a la vista previa en pantalla, reutilizando pares de contraste ya autorizados en §7.

### 10.1 Alcance y principios

1. **Legal primero**: todo campo fiscal obligatorio VE definido en M-16 (razón social, RIF, número de factura, fecha/hora, base imponible, IVA, total) se imprime con el tamaño y énfasis máximo de su bloque. Ninguna decisión estética puede degradar, ocultar o reducir un campo fiscal.
2. **Monocromo térmico**: el ticket físico usa SOLO negro sólido sobre papel térmico blanco. PROHIBIDO escala de grises, tramado (dithering) e inversión de video para texto (ver §10.9).
3. **Paleta cerrada (§0.1) se mantiene**: la vista previa en pantalla no introduce hex nuevos; reutiliza exclusivamente pares autorizados en §7.1/§7.2.
4. **Monoespaciado estructural**: todo el ticket (físico y preview) usa fuente monoespaciada — alineación de columnas de importes garantizada por diseño, equivalente térmico de la regla `tnum` de §2.1.
5. **Datos, no diseño**: la alícuota de IVA, la leyenda fiscal y los textos legales son DATOS del sistema (configurables), nunca valores fijos del diseño. El diseño define ubicación, tamaño y énfasis; el contenido legal requiere validación de Wilfredo (Legal) — ver §10.10 dependencias.
6. **Trazabilidad**: reimpresión y anulación se marcan de forma inequívoca y verificable a simple vista, conservando el 100% de los datos originales del comprobante (§10.8).

### 10.2 Formatos de impresión y grilla

Formatos M-16: **58mm** y **80mm** (impresión térmica). Métrica de referencia ESC/POS, cabezal 203 dpi (8 dots/mm):

| Especificación | 58mm | 80mm |
|----------------|------|------|
| Ancho de papel | 58mm | 80mm |
| Ancho útil de impresión | 48mm | 72mm |
| Resolución de cabezal | 203 dpi (8 dots/mm) | 203 dpi (8 dots/mm) |
| Fuente del cuerpo (Font A) | 12×24 dots = 1,5×3,0mm por carácter | ídem |
| **Columnas de cuerpo (Font A)** | **32 caracteres/línea** | **48 caracteres/línea** |
| Font B (9×17 dots = 1,13×2,13mm) | 42 col — SOLO pie no fiscal (§10.3) | 64 col — SOLO pie no fiscal |
| Pitch de línea | 30 dots = 3,75mm | 30 dots = 3,75mm |
| Margen lateral | 1mm por lado (driver) | 1mm por lado (driver) |
| Énfasis (ESC/POS) | `GS !` doble alto (DH); doble alto+ancho (DH+DW); `ESC E` doble golpe (B) | ídem |
| Corte | Corte total + 2 líneas de alimentación en blanco antes del corte (protección del cabezal) | ídem |

Reglas de grilla:

- La **tabla de columnas (32/48) es el contrato del layout**: es la vía canónica de implementación (comandos ESC/POS nativos, a consumir por la API de Nelson en F1). Si un proveedor imprime vía driver CSS, mantener los anchos de papel en mm y las zonas porcentuales equivalentes — no las columnas.
- **Font B PROHIBIDO para campos fiscales** (razón social, RIF, número de factura, fecha/hora, detalle, base, IVA, total): su glifo de 1,13×2,13mm no garantiza legibilidad de datos legales. Font B se permite únicamente en el pie no fiscal (agradecimiento, promoción), nunca en 58mm para texto que el cliente deba leer.
- Mayúsculas en todo el cuerpo del ticket (estándar térmico, mejora legibilidad en matriz de puntos). Codepage **CP850 obligatorio** (preserva á, é, í, ó, ú, ñ de la razón social — el nombre legal NO se normaliza); si el hardware no soporta CP850, se normaliza sin diacríticos y se registra hallazgo.
- Separadores de bloque: filas continuas de `-` (32/48 guiones). Filas de `*` reservadas EXCLUSIVAMENTE para marcar banners de variante (§10.8).

### 10.3 Tipografía monoespaciada y tokens

**Impresión térmica**: las impresoras ESC/POS traen las fuentes en ROM (Font A/B descritas en §10.2); el diseño especifica qué fuente, tamaño y énfasis usa cada bloque (tablas §10.4-§10.7). No se envían fuentes al hardware.

**Vista previa en pantalla (web, React)**: familia **JetBrains Mono** — monoespaciada de código abierto, dígitos inequívocos (`0`/`O`, `1`/`l` distinguibles), armoniza con Inter (§2) por altura-x y forma similar, y existe en pesos 400/700. Fallbacks del sistema. Peso 400 en cuerpo; 700 SOLO en banners y TOTAL (jerarquía fiscal justifica el bold; la regla "solo 400" de estética terminal NO aplica a un documento legal).

Tokens nuevos de §10 (implementación en `design/tokens/tokens.css`/`tokens.json` delegada a Noris, F0-05/F1 — ver §10.10):

| Token | Valor | Uso |
|-------|-------|-----|
| `--font-mono-ticket` | `'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace` | Fuente única del ticket (preview; equivalente térmico: Font A) |
| `--ticket-body` | 13px · 1.4 · 400 | Cuerpo del ticket (equivale a Font A) |
| `--ticket-caption` | 12px · 1.35 · 400 | Pie no fiscal (equivale a Font B) |
| `--ticket-title` | 16px · 1.3 · 700 | Razón social, "TICKET FISCAL" (equivale a DH/DH+DW) |
| `--ticket-banner` | 16px · 1.3 · 700 · uppercase · tracking 0.1em | Banners REIMPRESIÓN / ANULADO (equivale a DH+DW) |
| `--ticket-total` | 16px · 1.3 · 700 | Línea TOTAL (equivale a DH) |
| `--ticket-w-58` | 219px | Ancho de la vista previa 58mm (96dpi) |
| `--ticket-w-80` | 302px | Ancho de la vista previa 80mm (96dpi) |
| `--ticket-paper` | `#FFFFFF` (fijo, NO temático) | Papel térmico en preview: el ticket es artefacto físico blanco, no se tematiza en modo oscuro |
| `--ticket-ink` | `#212529` | Tinta de datos (15.43:1 sobre `#FFFFFF`, autorizado §7.1) |
| `--ticket-sep-ink` | `#6C757D` | Separadores en preview (4.69:1 sobre `#FFFFFF`, autorizado §7.1) |

Formato numérico (regla térmica de `tnum` §2.1):

- Moneda: `#.###,##` — punto para miles, coma decimal, 2 decimales (convención del mercado VE). Símbolo `Bs` solo en labels de totales (ahorro de columnas en 58mm).
- Cantidad: enteros para unidades (`2`); 3 decimales para artículos pesados (M-15): `0,750 KG`.
- Importes y cantidades SIEMPRE alineados a la derecha de su zona; descripción SIEMPRE a la izquierda. El preview web fija `font-variant-numeric: tabular-nums` además del monoespaciado (consistencia con §2.1).

### 10.4 Estructura de bloques y jerarquía

| Bloque | Contenido | Jerarquía / énfasis |
|--------|-----------|--------------------|
| A · Encabezado emisor | Razón social, RIF, dirección, teléfono | Razón social DH+DW centrada; RIF B centrado; dirección/teléfono normal |
| B · Identificación del comprobante | "TICKET FISCAL" (B o DH), serial de máquina fiscal, **número de factura** (B), fecha/hora de emisión, cliente / CONSUMIDOR FINAL | Número de factura en B (bold); resto normal, label a la izquierda |
| V · Banner de variante (condicional) | REIMPRESIÓN y/o ANULADO (§10.8) | DH+DW, enmarcado por filas de `*` |
| C · Detalle de la venta | Artículos: cantidad, descripción, precio unitario, importe | Normal; sublínea de cantidad×unitario en 58mm |
| D · Totales fiscales | Leyenda IVA, base imponible, IVA por alícuota, **TOTAL** | Leyenda B; base/IVA normal right-flush; **TOTAL DH (58mm) / DH+DW (80mm)** |
| E · Pie | Leyenda de variante al pie (si aplica), agradecimiento | Font B permitido (no fiscal) |
| F · Corte | 2 líneas en blanco + corte total | — |

Orden fijo de bloques: **A → B → [V] → C → D → [V-al-pie] → E → F**. El banner de variante se imprime DOS veces (arriba tras B, y abajo antes de E) para que sobreviva al desgarro del papel en cualquier extremo.

### 10.5 Mockup canónico — formato 58mm (32 columnas)

Leyenda de énfasis: `(DH)` doble alto, `(DH+DW)` doble alto+ancho, `(B)` bold. Mockup a 32 columnas exactas:

```
    BODEGON EL CENTRAL, C.A.          (DH+DW, centrado)
          J-31234567-8                (B, centrado)
  AV. PRINCIPAL, EDIF. CENTRAL
      LOCAL 4 - CARACAS 1040
       TEL: 0212-555-1234
********************************
          TICKET FISCAL             (B)
********************************
 MAQ. FISCAL: VSE-042723
 FACT. NRO: 001-00012345            (B)
 EMISION: 05/09/2026 14:32:05
 CLIENTE: CONSUMIDOR FINAL
--------------------------------
ARTICULO                  IMPORTE
LECHE ENTERA 1L SANCOR     12,00
  2,000 UN X 6,00
PAN CAMPESINO 500G          6,50
  1,000 UN X 6,50
QUESO BLANCO KG              8,10
  0,750 KG X 10,80
--------------------------------
    PRECIO CON IVA INCLUIDO       (B)
 BASE IMPONIBLE Bs         22,55
 IVA 16% Bs                  4,05
 TOTAL PAGAR Bs             26,60  (DH)
--------------------------------
      GRACIAS POR SU COMPRA
       ** BODEGAPP **              (Font B, no fiscal)
```

Zonas del bloque C (58mm) — contrato de columnas:

| Zona | Columnas (1-32) | Alineación |
|------|------------------|------------|
| Descripción | 1-22 | Izquierda; trunca/pasa a sublínea si excede 22 |
| Importe | 23-32 | Derecha (10 caracteres) |
| Sublínea `CANT UN X P.UNIT` | 3-19 | Izquierda, indentada 2 — solo si el artículo pesado (M-15) o descuento/recargo lo requiere; en unidades enteras se omite |

En 58mm el precio unitario NO tiene columna propia (no cabe con calidad legible): se resuelve con sublínea `CANT UN x P.UNIT`. El importe de renglón SIEMPRE está presente (campo fiscal del detalle).

### 10.6 Mockup canónico — formato 80mm (48 columnas)

```
            BODEGON EL CENTRAL, C.A.        (DH+DW, centrado)
                  J-31234567-8              (B, centrado)
     AV. PRINCIPAL, EDIF. CENTRAL, LOCAL 4
      CARACAS 1040 - DISTRITO CAPITAL
               TEL: 0212-555-1234
************************************************
                 TICKET FISCAL               (B)
 MAQ. FISCAL: VSE-042723
 FACT. NRO: 001-00012345                     (B)
 EMISION: 05/09/2026 14:32:05
 CLIENTE: CONSUMIDOR FINAL
------------------------------------------------
  CANT ARTICULO                  P.UNIT IMPORTE
 2,000 LECHE ENTERA 1L SANCOR      6,00   12,00
 1,000 PAN CAMPESINO 500G         6,50    6,50
 0,750 QUESO BLANCO KG           10,80    8,10
------------------------------------------------
             PRECIO CON IVA INCLUIDO          (B)
   BASE IMPONIBLE Bs                       22,55
   IVA 16% Bs                                4,05
   TOTAL PAGAR Bs                           26,60  (DH+DW)
------------------------------------------------
          GRACIAS POR SU COMPRA - BODEGAPP
```

Zonas del bloque C (80mm) — contrato de columnas:

| Zona | Columnas (1-48) | Ancho | Alineación |
|------|------------------|-------|------------|
| Cantidad | 1-6 | 6 | Derecha (`2,000` incluye 3 decimales de M-15) |
| Separador | 7 | 1 | — |
| Descripción | 8-31 | 24 | Izquierda; trunca a 24 + continuación en línea inferior indentada |
| Separador | 32 | 1 | — |
| Precio unitario | 33-40 | 8 | Derecha |
| Separador | 41 | 1 | — |
| Importe | 42-48 | 7 | Derecha |

En 80mm el precio unitario TIENE columna propia (ventaja del formato ancho); los artículos pesados (M-15) muestran la cantidad en la columna CANT sin sublínea.

### 10.7 Campos fiscales obligatorios (VE) — checklist

Baseline obligatorio según M-16; la columna "Validación legal" marca los campos cuya exigencia o redacción exacta requiere confirmación de Wilfredo (Legal) — el diseño los ubica y dimensiona ya, para que un cambio de redacción NO cambie el layout (principio 5 de §10.1: son datos configurables).

| # | Campo fiscal | Fuente de dato | Bloque | Énfasis | Validación legal |
|---|--------------|----------------|--------|---------|------------------|
| 1 | Razón social del emisor | M-01 Config. tienda | A | DH+DW centrado | OK (M-16) |
| 2 | RIF del emisor | M-01 | A | B centrado | OK (M-16) |
| 3 | Serial de máquina fiscal | Config. fiscal (payload F1) | B | Normal | ⚠ N-F009-04 (naturaleza del comprobante) |
| 4 | Número de factura | Contador fiscal (payload F1) | B | B | ⚠ N-F009-08 (formato del número) |
| 5 | Fecha y hora de emisión | Reloj del sistema/fiscal | B | Normal | OK (M-16) |
| 6 | Identificación del cliente o "CONSUMIDOR FINAL" | M-08/M-09 o default | B | Normal | ⚠ N-F009-04 |
| 7 | Detalle: descripción, cantidad, precio unitario, importe | Venta en curso | C | Normal | OK |
| 8 | Leyenda "PRECIO CON IVA INCLUIDO" | Config. (texto dato) | D | B | ⚠ N-F009-07 (redacción exacta) |
| 9 | Base imponible | Cálculo de la venta | D | Normal, right-flush | OK (M-16) |
| 10 | IVA (por alícuota) | Cálculo (alícuota = dato) | D | Normal, right-flush | ⚠ N-F009-07 (alícuotas aplicables) |
| 11 | TOTAL | Cálculo de la venta | D | DH (58mm) / DH+DW (80mm) | OK (M-16) |

Reglas del bloque D:

- Una fila por alícuota de IVA presente en la venta (ej. `IVA 16% Bs`, `IVA 8% Bs`): el diseño soporta N filas; qué alícuotas aplica la bodega es dato legal (N-F009-07).
- Montos right-flush a la columna límite (32/48); labels a la izquierda con un espacio de margen.
- La fila TOTAL usa la máxima jerarquía del ticket (§10.4); en 58mm es DH SIN doble ancho (`TOTAL PAGAR Bs 26,60` = 22 caracteres > 16 columnas visibles de DH+DW); en 80mm es DH+DW (`TOTAL PAGAR Bs 26,60` = 20 ≤ 24 columnas visibles).

### 10.8 Variantes: REIMPRESIÓN y ANULADO

Ambas variantes son marcaciones de un comprobante YA EMITIDO: los datos fiscales originales (bloques A-D) se reimprimen idénticos, sin omisión ni alteración. La variante SOLO agrega banners y metadatos de la operación (fecha, motivo, operador).

#### 10.8.1 Variante REIMPRESIÓN

- **Banner superior** (tras bloque B) e **inferior** (antes del pie E): la palabra `REIMPRESION` en DH+DW, centrada, enmarcada por filas de `*` (32/48). El asterisco está reservado a banners de variante (§10.2) — ningún otro bloque lo usa, para que la marca sea inequívoca a simple vista.
- Metadatos bajo el banner superior: `REIMPRESO: <fecha/hora de la reimpresión>` y `EMISION: <fecha/hora original>` (esta última ya existe en bloque B; se conserva).
- **Leyenda al pie**: texto legal de la reimpresión — DATO configurable; redacción exacta PENDIENTE Wilfredo (N-F009-05).

```
********************************
          REIMPRESION          (DH+DW, centrado)
********************************
 REIMPRESO: 05/09/2026 15:02:11
--------------------------------
     (bloques C y D idénticos)
--------------------------------
********************************
          REIMPRESION          (DH+DW, centrado)
********************************
 LEYENDA LEGAL DE REIMPRESION   (dato — N-F009-05)
```

#### 10.8.2 Variante ANULADO

- **Banner superior e inferior**: `ANULADO` en DH+DW, centrada, enmarcada por filas de `*` — mismo lenguaje visual que REIMPRESIÓN, palabra distinta (paralelismo reconocible).
- Metadatos bajo el banner superior: `ANULADO EL: <fecha/hora>`, `MOTIVO: <dato>`, `OPERADOR: <dato>`.
- **PROHIBIDO tachar, cubrir u oscurecer los datos fiscales** (sin marcas cruzadas sobre el detalle/totales): el comprobante anulado sigue siendo registro legal y debe permanecer 100% legible. La anulación se comunica por banners + metadatos, nunca destruyendo información.
- **Leyenda al pie**: "no válido como comprobante" — DATO configurable; redacción y relación con Nota de Crédito PENDIENTE Wilfredo (N-F009-06).

```
********************************
           ANULADO            (DH+DW, centrado)
********************************
 ANULADO EL: 05/09/2026 15:05:00
 MOTIVO: ERROR DE CAPTURA
 OPERADOR: ADMIN-01
--------------------------------
     (bloques C y D idénticos, legibles)
--------------------------------
********************************
           ANULADO            (DH+DW, centrado)
********************************
 LEYENDA LEGAL DE ANULACION     (dato — N-F009-06)
```

#### 10.8.3 Composición REIMPRESIÓN + ANULADO

Un ticket anulado que se reimprime muestra AMBOS banners apilados (primero ANULADO — estado del comprobante —, luego REIMPRESION — naturaleza de la copia), cada uno con sus filas de `*`. Los banners inferiores se apilan en el mismo orden. Regla: máximo 2 banners por posición (no existen otras variantes en M-16).

#### 10.8.4 Vista previa y acciones en la UI (flujo del operador)

- **Vista previa de ticket**: modal §5.7 con la maqueta del ticket a ancho `--ticket-w-58`/`--ticket-w-80` según la impresora configurada (selector de formato en Configuración, M-01). Papel `--ticket-paper` fijo blanco con tinta `--ticket-ink` (15.43:1 §7.1) — no se tematiza.
- Banners en preview (pares ya autorizados §7.1): REIMPRESIÓN → texto `#212529` sobre `#FFF6E4` (14.36:1); ANULADO → texto `#800020` sobre `#FFFFFF` (10.28:1).
- Acciones: **Imprimir** (botón primario §5.1), **Reimprimir** (secundario; deshabilitado si el ticket no está emitido; abre confirmación §5.7 mostrando el banner de preview), **Anular** (destructivo §5.1; requiere confirmación con motivo obligatorio — input §5.2). Anular jamás imprime automáticamente: el operador decide reimprimir la copia anulada.
- La vista previa del banner cumple foco/teclado estándar (§7.3 regla 5); el estado de variante se comunica con TEXTO (palabra REIMPRESION/ANULADO), nunca solo con color — el ticket físico es monocromo y el digital hereda la regla.

### 10.9 Contraste y accesibilidad en papel térmico

1. **Negro sólido = único color**: `#000000` sobre papel térmico blanco ≈ 21:1 (equivalente del par máximo §7). La densidad de impresión se configura en valor estándar/fijo de fábrica; PROHIBIDO el modo "económico/claro" para tickets fiscales. Prueba de aceptación QA: caracteres legibles sin esfuerzo a 30cm con luz de bodega tras 24h de emitido (descarte térmico).
2. **PROHIBIDO escala de grises y tramado** (`GS v 0` raster) para cualquier texto: el antialiasing no existe en térmica y el gris degrada a punteado ilegible. Logo/arte en el pie: monocromo puro o nada.
3. **PROHIBIDO inversión de video** (blanco sobre negro) en más de una línea: los bloques negros densos sobrecalientan el cabezal y empastan el papel. Los banners usan texto DH+DW con marco de `*`, nunca rectángulos negros.
4. **Tamaño mínimo legible**: Font A (1,5×3,0mm) para TODO lo fiscal; Font B solo pie no fiscal (§10.2). La razón social, número de factura y TOTAL usan énfasis mayor (§10.4) — son los tres datos que un cliente/funcionario busca primero.
5. **Copia digital ampliable** (accesibilidad funcional): el ticket se archiva en el historial digital (patrón M-08/M-09) renderizado como documento ampliable en pantalla con los tokens de preview (§10.3) — usuarios de baja visión leen el mismo contenido con zoom de navegador. El papel térmico desvanece con calor/luz: la copia digital es además respaldo del registro.
6. **Preview en pantalla**: pares de contraste documentados en §10.3/§10.8.4 — todos autorizados previamente en §7.1 (`#212529`/`#FFFFFF` 15.43, `#6C757D`/`#FFFFFF` 4.69, `#212529`/`#FFF6E4` 14.36, `#800020`/`#FFFFFF` 10.28). Sin hex nuevos (principio §0.1).

### 10.10 Gobernanza, contrato de datos y trazabilidad

**Gobernanza** (extiende §8):

- Los tokens de §10.3 se implementan en `design/tokens/tokens.css` y `tokens.json` — tarea de **Noris** (F0-05/F1), NO de esta entrega (alcance F0-09: solo `design-system.md`).
- Cambios a §10 requieren aprobación de **Cristian**; la redacción exacta de leyendas fiscales y los requisitos normativos requieren validación de **Wilfredo** (Legal) — hallazgos N-F009-04..08 (§ informe F0-09); QA de **Emilio** requerido antes de merge.
- Consumidores: **Nelson** (API/payload de impresión, F1) y **Noris** (preview/impresión frontend, F1).

**Contrato de datos del payload** (para Nelson, F1 — el layout consume estos campos):

| Campo | Ejemplo | Bloque |
|-------|---------|--------|
| `razon_social`, `rif`, `direccion`, `telefono` | M-01 | A |
| `serial_maquina_fiscal`, `numero_factura`, `fecha_emision`, `cliente` / `consumidor_final` | `VSE-042723` · `001-00012345` | B |
| `items[]: {cantidad, unidad, descripcion, precio_unitario, importe}` | `0,750 KG QUESO BLANCO` | C |
| `leyenda_iva`, `base_imponible`, `iva_por_alicuota[]: {alícuota, monto}`, `total` | `16%` · `4,05` | D |
| `variante: null \| reimpresion \| anulado \| ambas`, `fecha_variante`, `motivo`, `operador`, `leyenda_variante` | §10.8 | V/E |
| `formato: 58 \| 80` | selector de impresora | grilla §10.2 |

**Trazabilidad de decisiones de §10:**

| Decisión | Justificación |
|----------|---------------|
| JetBrains Mono en preview | Monoespaciada open source, dígitos inequívocos, armoniza con Inter (§2); peso 700 reservado a jerarquía fiscal (TOTAL/banners) |
| 32/48 columnas como contrato | Ancho útil ESC/POS ÷ glifo Font A (48mm/1,5mm=32; 72mm/1,5mm=48) — reproducible en cualquier térmica 203 dpi |
| Unitario sin columna en 58mm | 32 columnas no admiten 4 zonas legibles; sublínea `CANT X P.UNIT` es patrón estándar de ticket angosto |
| Font B prohibido en campos fiscales | Glifo 1,13×2,13mm insuficiente para datos legales; solo pie no fiscal |
| Banner = texto DH+DW + marco de `*`, nunca bloque negro | Cabezal térmico se daña con áreas densas (§10.9.3); `*` reservado a variantes = marca inequívoca |
| TOTAL: DH en 58mm, DH+DW en 80mm | En 58mm la línea completa no cabe en 16 columnas visibles de DH+DW; en 80mm sí (20 ≤ 24) |
| Papel de preview fijo blanco | El ticket es artefacto físico; tematizarlo oscuro falsearía el documento (contraste 15.43:1 §7.1) |
| Variante imprime datos originales íntegros + banners duplicados (arriba/abajo) | Registro legal inalterable (principio 6) + supervivencia al desgarro del papel |
| Leyendas/alícuotas como datos configurables | Cambios legales no alteran el layout; validación redactada por Wilfredo (N-F009-04..08) |
| Sin código de barras/QR del comprobante | M-16 no lo exige; M-04/M-05 son escaneo de productos. Anotado como posible backlog futuro |

---

### Anexo — Trazabilidad de decisiones

| Decisión | Justificación |
|----------|---------------|
| Surface claro `#FFFFFF` | §4 no define tarjeta en claro; blanco puro jerarquiza sobre `#F8F9FA` y es el par de mayor contraste (15.43) |
| Border claro = `#6C757D` al 25% | §4 no define borde en claro; derivación algorítmica del gris oficial mantiene paleta cerrada |
| Destructivo claro = `#800020` | Distinguir "eliminar" del CTA primario `#C41230` sin introducir rojo nuevo |
| Texto sobre secundario/accent oscuro = `#121212` | Único par AA (12.25 / 9.31); blanco falla (1.73 sería amarillo; 2.01 esmeralda) |
| Badge agotado oscuro outline | `#FFFFFF` sobre `#E53935` = 4.23 < 4.5; variante outline garantiza AA en texto pequeño |
| Flat Design + densidad alta | Validado con ui-ux-pro-max para dashboards de inventario; paleta y fuentes del skill DESCARTADAS por directiva del inversor |
| Alerta "Advertencia": cuerpo `--color-text-primary`, chip ámbar solo para icono/título | Remedición QA F0-01 OBS-03: `#121212` sobre mezcla 12% de ámbar = 1.49:1 ilegible en oscuro; `#FFFFFF` sobre `#39331F` = 12.60:1 AA y `#212529` sobre `#FFF6E4` = 14.36:1 AA |
| Alerta "Info" claro: cuerpo `--color-text-primary` (`#212529`) | Remedición O-N-001: `#6C757D` sobre `#F5F5F5` = 4.30:1 fallaba AA; `#212529` sobre `#F5F5F5` = 14.15:1 AA |
