import { act, renderHook, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { useTiendaConfig } from './useTiendaConfig';
import { tiendaApi, type ApiErrorLike } from '@/lib/tiendaApi';
import type { StoreConfig, StoreConfigUpdatePayload } from '@/types/tienda';

vi.mock('@/lib/tiendaApi', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/lib/tiendaApi')>();
  return {
    ...actual,
    tiendaApi: {
      getConfig: vi.fn(),
      updateConfig: vi.fn(),
    },
  };
});

const getConfigMock = vi.mocked(tiendaApi.getConfig);
const updateConfigMock = vi.mocked(tiendaApi.updateConfig);

const CONFIG: StoreConfig = {
  id: 'uuid-config',
  tenant_id: 'uuid-tenant',
  nombre_comercial: 'Bodega Central',
  rif: 'J123456789',
  razon_social: 'Bodega Central C.A.',
  direccion: 'Av. Principal',
  direccion_fiscal: null,
  telefono: '02125551122',
  moneda: 'VES',
  creado: '2026-09-01T10:00:00Z',
  actualizado: '2026-09-02T10:00:00Z',
};

const PAYLOAD: StoreConfigUpdatePayload = {
  nombre_comercial: 'Bodega Central',
  rif: 'J123456789',
  razon_social: 'Bodega Central C.A.',
  direccion: 'Av. Principal',
  direccion_fiscal: null,
  telefono: '02125551122',
  moneda: 'VES',
};

function apiError(status: number, mensaje: string): ApiErrorLike {
  const error = new Error(mensaje) as ApiErrorLike;
  error.status = status;
  error.codigo = status === 404 ? 'RECURSO_NO_ENCONTRADO' : 'VALIDACION_ERROR';
  return error;
}

describe('useTiendaConfig', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('loads the tenant config via GET on mount', async () => {
    getConfigMock.mockResolvedValue(CONFIG);

    const { result } = renderHook(() => useTiendaConfig());

    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(result.current.config).toEqual(CONFIG);
    expect(result.current.loadError).toBeNull();
    expect(getConfigMock).toHaveBeenCalledOnce();
  });

  it('treats 404 as create mode (null config, no error)', async () => {
    getConfigMock.mockRejectedValue(apiError(404, 'No existe configuración de tienda para este tenant.'));

    const { result } = renderHook(() => useTiendaConfig());

    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(result.current.config).toBeNull();
    expect(result.current.loadError).toBeNull();
  });

  it('surfaces load errors other than 404', async () => {
    getConfigMock.mockRejectedValue(apiError(500, 'Ocurrió un error inesperado.'));

    const { result } = renderHook(() => useTiendaConfig());

    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(result.current.loadError?.status).toBe(500);
    expect(result.current.config).toBeNull();
  });

  it('saves via PUT and updates the config on success', async () => {
    getConfigMock.mockResolvedValue(CONFIG);
    const saved: StoreConfig = { ...CONFIG, telefono: '02129998877' };
    updateConfigMock.mockResolvedValue(saved);

    const { result } = renderHook(() => useTiendaConfig());
    await waitFor(() => expect(result.current.isLoading).toBe(false));

    await act(async () => {
      await result.current.save({ ...PAYLOAD, telefono: '02129998877' });
    });

    expect(updateConfigMock).toHaveBeenCalledWith({ ...PAYLOAD, telefono: '02129998877' });
    expect(result.current.config).toEqual(saved);
    expect(result.current.isSuccess).toBe(true);
    expect(result.current.saveError).toBeNull();
    expect(result.current.isSaving).toBe(false);
  });

  it('exposes save errors without throwing the page away', async () => {
    getConfigMock.mockResolvedValue(CONFIG);
    updateConfigMock.mockRejectedValue(apiError(422, 'Los datos enviados no son válidos.'));

    const { result } = renderHook(() => useTiendaConfig());
    await waitFor(() => expect(result.current.isLoading).toBe(false));

    await act(async () => {
      await expect(result.current.save(PAYLOAD)).rejects.toThrow('Los datos enviados no son válidos.');
    });

    expect(result.current.saveError?.status).toBe(422);
    expect(result.current.isSuccess).toBe(false);
    expect(result.current.config).toEqual(CONFIG);
  });

  it('clears the success banner on dismissSuccess', async () => {
    getConfigMock.mockResolvedValue(CONFIG);
    updateConfigMock.mockResolvedValue(CONFIG);

    const { result } = renderHook(() => useTiendaConfig());
    await waitFor(() => expect(result.current.isLoading).toBe(false));

    await act(async () => {
      await result.current.save(PAYLOAD);
    });
    expect(result.current.isSuccess).toBe(true);

    act(() => {
      result.current.dismissSuccess();
    });
    expect(result.current.isSuccess).toBe(false);
  });
});
