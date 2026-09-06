import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { ConfiguracionTiendaPage } from './ConfiguracionTiendaPage';
import { AuthProvider } from '@/context/AuthContext';
import { tiendaApi } from '@/lib/tiendaApi';
import type { StoreConfig } from '@/types/tienda';

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
  razon_social: null,
  direccion: 'Av. Principal',
  direccion_fiscal: null,
  telefono: null,
  moneda: 'VES',
  creado: '2026-09-01T10:00:00Z',
  actualizado: '2026-09-02T10:00:00Z',
};

function renderPage() {
  return render(
    <MemoryRouter initialEntries={['/configuracion']}>
      <AuthProvider>
        <ConfiguracionTiendaPage />
      </AuthProvider>
    </MemoryRouter>,
  );
}

describe('ConfiguracionTiendaPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows a loading state while the config is fetched', () => {
    getConfigMock.mockReturnValue(new Promise(() => {}) as never);
    renderPage();

    expect(screen.getByRole('status')).toHaveTextContent('Cargando datos de la tienda…');
    expect(screen.queryByRole('button', { name: /guardar/i })).not.toBeInTheDocument();
  });

  it('renders the form prefilled from GET /tienda/configuracion', async () => {
    getConfigMock.mockResolvedValue(CONFIG);
    renderPage();

    await waitFor(() =>
      expect(screen.getByLabelText('Nombre comercial')).toHaveValue('Bodega Central'),
    );
    expect(screen.getByLabelText('RIF')).toHaveValue('J123456789');
    expect(screen.getByLabelText('Dirección')).toHaveValue('Av. Principal');
    expect(screen.getByLabelText('Moneda principal')).toHaveValue('VES');
  });

  it('renders an empty create form when the API answers 404 (no config saved yet)', async () => {
    getConfigMock.mockRejectedValue(
      Object.assign(new Error('No existe configuración de tienda para este tenant.'), {
        status: 404,
        codigo: 'RECURSO_NO_ENCONTRADO',
      }),
    );
    renderPage();

    await waitFor(() => expect(screen.getByLabelText('Nombre comercial')).toHaveValue(''));
    expect(screen.getByRole('button', { name: 'Guardar configuración' })).toBeInTheDocument();
  });

  it('shows an error banner when the load fails with a non-404 error', async () => {
    getConfigMock.mockRejectedValue(
      Object.assign(new Error('Ocurrió un error inesperado.'), { status: 500 }),
    );
    renderPage();

    await waitFor(() =>
      expect(screen.getByText(/No pudimos cargar la configuración de tu tienda/i)).toBeInTheDocument(),
    );
  });

  it('blocks submit and shows field errors when validation fails', async () => {
    getConfigMock.mockResolvedValue(CONFIG);
    const user = userEvent.setup();
    renderPage();

    await waitFor(() =>
      expect(screen.getByLabelText('Nombre comercial')).toHaveValue('Bodega Central'),
    );
    await user.clear(screen.getByLabelText('Nombre comercial'));
    await user.type(screen.getByLabelText('RIF'), '12345678');
    await user.click(screen.getByRole('button', { name: /guardar cambios/i }));

    expect(
      await screen.findByText('El nombre comercial es obligatorio.'),
    ).toBeInTheDocument();
    expect(
      screen.getByText('El RIF debe tener el formato venezolano, por ejemplo J-12345678-9.'),
    ).toBeInTheDocument();
    expect(updateConfigMock).not.toHaveBeenCalled();
  });

  it('saves via PUT with a normalized payload and shows a success banner', async () => {
    getConfigMock.mockResolvedValue(CONFIG);
    updateConfigMock.mockResolvedValue({ ...CONFIG, telefono: '02125551122' });
    const user = userEvent.setup();
    renderPage();

    await waitFor(() =>
      expect(screen.getByLabelText('Nombre comercial')).toHaveValue('Bodega Central'),
    );
    await user.type(screen.getByLabelText('Teléfono'), '02125551122');
    await user.click(screen.getByRole('button', { name: /guardar cambios/i }));

    await waitFor(() =>
      expect(
        screen.getByText('Configuración guardada correctamente.'),
      ).toBeInTheDocument(),
    );
    expect(updateConfigMock).toHaveBeenCalledWith({
      nombre_comercial: 'Bodega Central',
      rif: 'J123456789',
      razon_social: null,
      direccion: 'Av. Principal',
      direccion_fiscal: null,
      telefono: '02125551122',
      moneda: 'VES',
    });
  });

  it('shows the server error message when the PUT fails', async () => {
    getConfigMock.mockResolvedValue(CONFIG);
    updateConfigMock.mockRejectedValue(
      Object.assign(new Error('Los datos enviados no son válidos.'), { status: 422 }),
    );
    const user = userEvent.setup();
    renderPage();

    await waitFor(() =>
      expect(screen.getByLabelText('Nombre comercial')).toHaveValue('Bodega Central'),
    );
    await user.clear(screen.getByLabelText('Nombre comercial'));
    await user.type(screen.getByLabelText('Nombre comercial'), 'Bodega Nueva');
    await user.click(screen.getByRole('button', { name: /guardar cambios/i }));

    await waitFor(() =>
      expect(screen.getByText('Los datos enviados no son válidos.')).toBeInTheDocument(),
    );
  });

  it('maps 422 validation detalles for rif/moneda to their fields', async () => {
    getConfigMock.mockResolvedValue(CONFIG);
    updateConfigMock.mockRejectedValue(
      Object.assign(
        new Error('Los datos enviados no son válidos.'),
        {
          status: 422,
          detalles: [{ campo: 'body.rif', problema: 'Value error, El RIF debe tener el formato venezolano' }],
        },
      ),
    );
    const user = userEvent.setup();
    renderPage();

    await waitFor(() =>
      expect(screen.getByLabelText('Nombre comercial')).toHaveValue('Bodega Central'),
    );
    await user.clear(screen.getByLabelText('RIF'));
    // Valid per the client pattern (J + 8 digits + check digit) — the
    // backend still rejects it, e.g. a stricter check-digit algorithm.
    await user.type(screen.getByLabelText('RIF'), 'J12345678-0');
    await user.click(screen.getByRole('button', { name: /guardar cambios/i }));

    await waitFor(() => expect(updateConfigMock).toHaveBeenCalledOnce());
    const rifField = screen.getByLabelText('RIF');
    const group = rifField.closest('div') as HTMLElement;
    expect(
      await within(group).findByText('Los datos enviados no son válidos.'),
    ).toBeInTheDocument();
  });
});
