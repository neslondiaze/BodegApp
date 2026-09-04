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

Encabezado: fondo hover de superficie, texto `--font-caption` peso 600 `--color-text-secondary`, alto 40px. Filas: alto 48px (44px mínimo táctil), borde inferior 1px `--color-border`, texto `--font-data` para números. Columnas canónicas de inventario: Producto · Código de barras (M-04) · Stock · Mínimo · Precio Bs · Precio USD (tasa BCV) · Estado · Acciones. Filas con stock bajo/agotado llevan badge (§5.5) además de color — nunca solo color. Ordenación por columna con indicador textual (asc/desc). Vacío: mensaje centrado + CTA de alta.

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
