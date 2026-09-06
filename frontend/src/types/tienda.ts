/**
 * Store configuration API types (M-01) — mirrors the real F1-03
 * backend schemas (backend/app/schemas/store_config.py):
 * only nombre_comercial is required so a tenant can save partial
 * configuration; fiscal fields are validated at ticket print time (M-16).
 */

export interface StoreConfig {
  id: string;
  tenant_id: string;
  nombre_comercial: string;
  rif: string | null;
  razon_social: string | null;
  direccion: string | null;
  direccion_fiscal: string | null;
  telefono: string | null;
  moneda: 'VES' | 'USD';
  creado: string;
  actualizado: string;
}

/** PUT /api/v1/tienda/configuracion request body (full replace). */
export interface StoreConfigUpdatePayload {
  nombre_comercial: string;
  rif: string | null;
  razon_social: string | null;
  direccion: string | null;
  telefono: string | null;
  direccion_fiscal: string | null;
  moneda: 'VES' | 'USD';
}
