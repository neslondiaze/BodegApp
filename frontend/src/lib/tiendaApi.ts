import { isAxiosError } from 'axios';
import { apiClient } from '@/lib/apiClient';
import type { StoreConfig, StoreConfigUpdatePayload } from '@/types/tienda';

/**
 * Tienda API module — thin typed wrapper over GET/PUT
 * /api/v1/tienda/configuracion (F1-03, per-tenant singleton).
 *
 * Page-level concerns live in the hook, not here: this module only
 * translates transport errors into ApiErrorLike shapes so the UI never
 * depends on axios internals.
 */

/** Uniform error envelope from the integration contract §3.2. */
export interface ApiErrorDetail {
  campo?: string;
  problema?: string;
}

export interface ApiErrorLike extends Error {
  status?: number;
  codigo?: string;
  detalles?: ApiErrorDetail[] | null;
}

const RIF_PATTERN = /^[VEJPG]-?\d{7,9}-?\d$/;
export const VALID_CURRENCIES = ['VES', 'USD'] as const;

export function isValidRif(value: string): boolean {
  return RIF_PATTERN.test(value.trim().toUpperCase());
}

/** Normalize a valid RIF to the dash-less form the backend stores. */
export function normalizeRif(value: string): string {
  return value.trim().toUpperCase().replace(/-/g, '');
}

export function toApiError(error: unknown): ApiErrorLike {
  if (isAxiosError<ApiErrorEnvelope>(error)) {
    const body = error.response?.data?.error;
    const apiError = new Error(body?.mensaje ?? error.message) as ApiErrorLike;
    apiError.status = error.response?.status;
    apiError.codigo = body?.codigo;
    apiError.detalles = body?.detalles ?? null;
    return apiError;
  }
  if (error instanceof Error) return error as ApiErrorLike;
  return new Error('Error de red inesperado.');
}

interface ApiErrorEnvelope {
  error?: {
    codigo?: string;
    mensaje?: string;
    detalles?: ApiErrorDetail[];
    request_id?: string;
  };
}

export const tiendaApi = {
  /** GET the tenant's config. 404 means "not saved yet" (create mode). */
  async getConfig(): Promise<StoreConfig> {
    const { data } = await apiClient.get<StoreConfig>('/tienda/configuracion');
    return data;
  },

  /** PUT full-replace; the backend upserts the per-tenant singleton. */
  async updateConfig(payload: StoreConfigUpdatePayload): Promise<StoreConfig> {
    const { data } = await apiClient.put<StoreConfig>('/tienda/configuracion', payload);
    return data;
  },
};
