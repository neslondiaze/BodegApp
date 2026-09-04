# BodegApp — Requerimientos Funcionales (Fuente de Verdad)

> Extraído de `Requerimientos para BodegApp.odt` (documento del inversor, 01/09/2026).
> Toda tarea del equipo debe trazarse a un ítem de este documento.

## 1. Definición del Producto

Sistema de inventario de productos para bodegas (mercado venezolano: bodegones, compras de conveniencia, abarrotes), **multi-tenant**.

## 2. Stack Tecnológico Mandatario

| # | Componente | Tecnología |
|---|-----------|------------|
| 0-1 | Backend | FastAPI (Python 3.12), PostgreSQL, autenticación JWT RS256 |
| 0-2 | Frontend | React 19 + Vite + TailwindCSS, routing protegido, arquitectura de tokens dual (contratante/trabajo) |
| 0-3 | Microservicio tiempo real | `operational-stream` en Go (Fase II) — ingesta operacional vía WebSocket |
| 0-4 | Infraestructura | docker-compose.yml endurecido (política Sentinel Shield v1.0): API, Frontend, PostgreSQL, Zero Trust, secrets de Docker |
| 0-5 | Modelo | Aplicación Multi-Tenant |

## 3. Módulos Funcionales (Alcance)

| ID | Módulo | Descripción |
|----|--------|-------------|
| M-01 | Configuración de Tienda | Datos de la tienda por tenant |
| M-02 | CRUD Productos | Alta/baja/modificación/consulta de productos |
| M-03 | CRUD Proveedores | Gestión de proveedores |
| M-04 | Lector código de barras | Escaneo EAN/UPC |
| M-05 | Lector QR | Escaneo de códigos QR |
| M-06 | Alerta mínimo de productos | Notificación cuando stock < mínimo definido |
| M-07 | Reporte de compras | Reporte para realizar compras (basado en stock y mínimos) |
| M-08 | CRUD Fiados | Ventas a crédito con campo **abono a cuenta** y campo **fecha de pago** |
| M-09 | Historial de fiados | Registro histórico de fiados y abonos |
| M-10 | Scraping BCV | Scraping de https://www.bcv.org.ve/ para tipo de cambio USD/Bs |
| M-11 | Actualización dólar BCV | Actualización automática de tasa desde BCV |
| M-12 | Historial tipo de cambio | Histórico de tasas capturadas |
| M-13 | Configuración scraping | Programación del scraping por días y horas |
| M-14 | Diseño de promociones WhatsApp | Módulo de diseño de promociones para envío por WhatsApp |
| M-15 | Integración peso electrónico | Balanza digital vía USB, RJ45 o RS-232 (Serial) |

## 4. Identidad Visual (Definida por el Inversor)

### Modo Claro
| Rol | Color | Hex |
|-----|-------|-----|
| Primario (CTA, logo, nav) | Rojo Vitalidad / Vinotinto | `#C41230` / `#800020` |
| Secundario (ofertas, badges) | Amarillo Oro | `#FFB81C` |
| Acento (stock OK, éxito pago) | Verde Frescura | `#2E7D32` |
| Fondo | Blanco grisáceo | `#F8F9FA` |
| Texto principal | Gris casi negro | `#212529` |
| Texto secundario | Gris medio | `#6C757D` |

### Modo Oscuro
| Rol | Color | Hex |
|-----|-------|-----|
| Fondo base | Gris casi negro | `#121212` |
| Tarjetas/contenedores | Gris elevado | `#1E1E1E` |
| Primario | Rojo suave | `#E53935` |
| Secundario | Amarillo ámbar | `#FFCA28` |
| Acento | Verde esmeralda claro | `#81C784` |
| Texto principal | Blanco | `#FFFFFF` / `#E0E0E0` |
| Texto secundario | Gris medio | `#9E9E9E` |
| Bordes/separadores | Gris sutil | `#2C2C2C` |

### Tipografía
- **Headlines** (títulos, categorías, nombres de tiendas): Plus Jakarta Sans o Cabinet Grotesk
- **Body/UI** (textos, precios, botones): Inter o SF Pro Display

### Referencia visual
- `design/referencias/modelo-referencia.png` — imagen adjunta por el inversor ("Modelo referencia"). Analizado en `design/design-system.md` §9 (inventario de zonas, elementos conservados/descartados y mejoras web del POS legacy).

## 5. Consideraciones del Mercado (Venezuela)

- Fiados (ventas a crédito) son operación central del negocio → módulo de primera clase.
- Tasa BCV USD/Bs impacta precios → scraping e historial son críticos.
- WhatsApp es canal principal de promociones.
- Balanzas con puerto serial RS-232 siguen siendo comunes en bodegas.
