# BodegApp — Checklist de Prototipado en Penpot (F0-01)

> Responsable: Nordanis (UI/UX) · Fuente de tokens: `design/design-system.md` + `design/tokens/`
> Regla: cada pantalla se prototipa en AMBOS temas (claro/oscuro) usando exclusivamente los tokens oficiales (REQUERIMIENTOS.md §4).

## Antes de empezar (setup del archivo Penpot)

- [ ] Crear archivo Penpot "BodegApp — Design System" con página "01 · Tokens"
- [ ] Cargar tipografías: Plus Jakarta Sans (600/700/800) e Inter (400/500/600/700)
- [ ] Crear estilos de color por tema (claro/oscuro) con los tokens de `design-system.md` §1
- [ ] Página "02 · Componentes": botones (primario/secundario/ghost/destructivo, 3 tamaños × 5 estados), inputs, badges de stock, alertas — según §5
- [ ] Página "03 · Pantallas": las de la checklist siguiente

## Checklist de pantallas

### 1. Login
- [ ] Pantalla de acceso con logo (primario `#C41230` / `#E53935`), campos usuario/contraseña con labels visibles
- [ ] Botón primario `lg` full-width (target táctil 48px)
- [ ] Estado de error de credenciales (alerta error §5.6) y estado loading del botón
- [ ] Ambos temas

### 2. Dashboard
- [ ] Topbar con nombre de tienda + indicador de tasa BCV + selector de tema
- [ ] Sidebar completo (7 secciones) con item activo según §5.8
- [ ] Cards de resumen: total productos · productos con stock bajo (badge ámbar) · agotados (badge rojo) · fiados pendientes (monto en `tnum`)
- [ ] Última tasa BCV capturada con fecha (M-10/M-11)
- [ ] Ambos temas

### 3. Productos
- [ ] Tabla de inventario completa según §5.4: Producto · Código de barras · Stock · Mínimo · Precio Bs · Precio USD · Estado (badge §5.5) · Acciones
- [ ] Filtros por categoría y estado de stock; buscador
- [ ] Estado vacío de tabla con CTA de alta
- [ ] Modal de alta/edición de producto (§5.7) con escaneo de código (M-04)
- [ ] Ambos temas · responsive: en <768px la tabla pasa a lista de cards (§5.3)

### 4. Proveedores
- [ ] Tabla: Nombre · RIF/identificación · Teléfono (CTA WhatsApp) · Productos asociados · Acciones
- [ ] Modal de alta/edición
- [ ] Ambos temas

### 5. Fiados
- [ ] Tabla de fiados activos: Cliente · Monto total · Abonado · Saldo · Fecha de pago · Estado
- [ ] Badge de estado de fiado (al día / vencido) usando semántica accent/destructive
- [ ] Modal "Registrar abono" con input de monto (tnum, alineación derecha) y confirmación de éxito (alerta éxito §5.6)
- [ ] Historial de fiados y abonos (M-09) como vista secundaria
- [ ] Ambos temas

### 6. Tipo de cambio
- [ ] Tasa BCV actual en grande (`--font-price`) + fecha/hora de última captura
- [ ] Gráfico/histórico de tasas (M-12) con leyenda y tooltip
- [ ] Configuración de scraping: días y horas (M-13) con selector visible; estado del scheduler (activo/inactivo)
- [ ] Alerta de fallo de scraping (error §5.6)
- [ ] Ambos temas

### 7. Promociones
- [ ] Galería de plantillas de promoción WhatsApp (M-14) con preview tipo chat
- [ ] Editor de plantilla: producto en oferta (badge secondary), precio con tasa aplicada, copy del mensaje
- [ ] Ambos temas

## Criterios de aceptación del prototipo

1. Cero hex fuera de los tokens oficiales §4 (verificación con el inspector de Penpot).
2. Contraste de texto verificado con el plugin de accesibilidad de Penpot: sin combinaciones prohibidas (§7 del design system: blanco/amarillo, blanco/esmeralda, texto pequeño gris sobre `#F8F9FA`).
3. Navegación completa por flujo: Login → Dashboard → cada módulo → volver.
4. Componentes instanciados desde la página de componentes (sin dibujos ad-hoc por pantalla).
5. Nombres de pantallas en español: `Login`, `Dashboard`, `Productos`, `Proveedores`, `Fiados`, `Tipo de cambio`, `Promociones`.
6. Los flujos de Fiados y Tipo de cambio incluyen la variante de error (fallo de abono, fallo de scraping).

## Fuera de alcance de este prototipo

- Configuración de tienda (M-01): reutiliza patrones de modal + inputs de Proveedores; se prototipa en Fase 1 si Cristian lo requiere.
- Lector de código de barras/QR (M-04/M-05) y balanza (M-15): hardware, Fase 3.
- Reporte de compras PDF (M-07): depende del diseño BI de Morloy (F1-07).
