import { useEffect, useMemo, useState, type FormEvent } from 'react';
import { Alert } from '@/components/feedback/Alert';
import { SelectField, TextField } from '@/components/forms/FormField';
import { useTiendaConfig } from '@/hooks/useTiendaConfig';
import { isValidRif, normalizeRif, VALID_CURRENCIES } from '@/lib/tiendaApi';
import type { StoreConfigUpdatePayload } from '@/types/tienda';

/**
 * Configuración de Tienda (M-01) — first inventory screen; sets the
 * pattern for the CRUD screens that follow (form primitives + API hook).
 *
 * Loads via GET /api/v1/tienda/configuracion (404 → empty create form),
 * saves the whole form via PUT (backend upserts the tenant singleton).
 * Client validation mirrors backend rules (store_config.py): required
 * nombre_comercial ≤255 chars, Venezuelan RIF pattern, moneda VES|USD.
 */

interface FormState {
  nombre_comercial: string;
  rif: string;
  razon_social: string;
  direccion: string;
  direccion_fiscal: string;
  telefono: string;
  moneda: string;
}

const EMPTY_FORM: FormState = {
  nombre_comercial: '',
  rif: '',
  razon_social: '',
  direccion: '',
  direccion_fiscal: '',
  telefono: '',
  moneda: 'VES',
};

const RIF_HELP = 'Formato venezolano, por ejemplo J-12345678-9. Se guarda sin guiones.';

type FieldErrors = Partial<Record<keyof FormState, string>>;

function validate(form: FormState): FieldErrors {
  const errors: FieldErrors = {};

  const nombre = form.nombre_comercial.trim();
  if (nombre === '') {
    errors.nombre_comercial = 'El nombre comercial es obligatorio.';
  } else if (nombre.length > 255) {
    errors.nombre_comercial = 'El nombre comercial no puede superar 255 caracteres.';
  }

  const rif = form.rif.trim();
  if (rif !== '' && !isValidRif(rif)) {
    errors.rif = 'El RIF debe tener el formato venezolano, por ejemplo J-12345678-9.';
  }

  if (form.razon_social.trim().length > 255) {
    errors.razon_social = 'La razón social no puede superar 255 caracteres.';
  }
  if (form.direccion.trim().length > 255) {
    errors.direccion = 'La dirección no puede superar 255 caracteres.';
  }
  if (form.direccion_fiscal.trim().length > 255) {
    errors.direccion_fiscal = 'La dirección fiscal no puede superar 255 caracteres.';
  }
  if (form.telefono.trim().length > 50) {
    errors.telefono = 'El teléfono no puede superar 50 caracteres.';
  }

  return errors;
}

/** Trim and null-ize empty optionals so PUT sends the backend's "absent = None" contract. */
function toPayload(form: FormState): StoreConfigUpdatePayload {
  return {
    nombre_comercial: form.nombre_comercial.trim(),
    rif: form.rif.trim() === '' ? null : normalizeRif(form.rif),
    razon_social: form.razon_social.trim() === '' ? null : form.razon_social.trim(),
    direccion: form.direccion.trim() === '' ? null : form.direccion.trim(),
    direccion_fiscal: form.direccion_fiscal.trim() === '' ? null : form.direccion_fiscal.trim(),
    telefono: form.telefono.trim() === '' ? null : form.telefono.trim(),
    moneda: form.moneda === 'USD' ? 'USD' : 'VES',
  };
}

export function ConfiguracionTiendaPage() {
  const { config, isLoading, isSaving, isSuccess, loadError, saveError, save, dismissSuccess } =
    useTiendaConfig();

  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [errors, setErrors] = useState<FieldErrors>({});

  // Hydrate the form once the GET resolves (config === null → create mode).
  useEffect(() => {
    if (isLoading) return;
    if (!config) return;
    setForm({
      nombre_comercial: config.nombre_comercial,
      rif: config.rif ?? '',
      razon_social: config.razon_social ?? '',
      direccion: config.direccion ?? '',
      direccion_fiscal: config.direccion_fiscal ?? '',
      telefono: config.telefono ?? '',
      moneda: config.moneda,
    });
  }, [config, isLoading]);

  const isCreateMode = !isLoading && !config;

  const setField = (field: keyof FormState) => (value: string) => {
    setForm((current) => ({ ...current, [field]: value }));
  };

  const isDirty = useMemo(() => {
    if (isLoading) return false;
    const payload = toPayload(form);
    if (!config) return payload.nombre_comercial !== '';
    return (
      payload.nombre_comercial !== config.nombre_comercial ||
      payload.rif !== config.rif ||
      payload.razon_social !== config.razon_social ||
      payload.direccion !== config.direccion ||
      payload.direccion_fiscal !== config.direccion_fiscal ||
      payload.telefono !== config.telefono ||
      payload.moneda !== config.moneda
    );
  }, [form, config, isLoading]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    dismissSuccess();

    const nextErrors = validate(form);
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length > 0) return;

    try {
      await save(toPayload(form));
      setErrors({});
    } catch {
      // saveError state drives the banner; the server mensaje is
      // contract-guaranteed Spanish end-user copy.
    }
  };

  const serverFieldErrors: FieldErrors = useMemo(() => {
    if (!saveError?.detalles) return {};
    const mapped: FieldErrors = {};
    for (const detalle of saveError.detalles) {
      const campo = detalle.campo?.replace(/^body\./, '');
      if (campo && (campo === 'rif' || campo === 'moneda') && detalle.problema) {
        // Prefer the human mensaje from the backend over the raw problema.
        mapped[campo] = saveError.message || detalle.problema;
      }
    }
    return mapped;
  }, [saveError]);

  const hasServerFieldErrors = Object.keys(serverFieldErrors).length > 0;

  if (isLoading) {
    return (
      <section aria-labelledby="config-tienda-title" aria-busy="true">
        <h1 id="config-tienda-title" className="font-headline text-2xl font-bold tracking-tight text-content-base">
          Configuración de tienda
        </h1>
        <p className="mt-2 text-sm text-content-muted" role="status">
          Cargando datos de la tienda…
        </p>
      </section>
    );
  }

  if (loadError) {
    return (
      <section aria-labelledby="config-tienda-title">
        <h1 id="config-tienda-title" className="font-headline text-2xl font-bold tracking-tight text-content-base">
          Configuración de tienda
        </h1>
        <div className="mt-4">
          <Alert variant="error">
            No pudimos cargar la configuración de tu tienda. {loadError.message} Intentá de nuevo en unos
            minutos.
          </Alert>
        </div>
      </section>
    );
  }

  const mergedErrors: FieldErrors = { ...errors, ...serverFieldErrors };

  return (
    <section aria-labelledby="config-tienda-title">
      <div className="mb-6">
        <h1
          id="config-tienda-title"
          className="font-headline text-2xl font-bold tracking-tight text-content-base"
        >
          Configuración de tienda
        </h1>
        <p className="mt-1 text-sm text-content-muted">
          {isCreateMode
            ? 'Completá los datos de tu bodega. Solo el nombre comercial es obligatorio; el resto lo podés terminar después.'
            : 'Datos con los que opera tu bodega: aparecen en la app y en los tickets.'}
        </p>
      </div>

      {isSuccess && (
        <div className="mb-4">
          <Alert variant="success" onDismiss={dismissSuccess}>
            Configuración guardada correctamente.
          </Alert>
        </div>
      )}
      {saveError && !hasServerFieldErrors && (
        <div className="mb-4">
          <Alert variant="error">
            {saveError.message || 'No pudimos guardar la configuración. Intentá de nuevo.'}
          </Alert>
        </div>
      )}

      <form
        onSubmit={handleSubmit}
        noValidate
        className="space-y-5 rounded-2xl border border-border-subtle bg-surface-card p-6"
      >
        <TextField
          label="Nombre comercial"
          name="nombre_comercial"
          autoComplete="organization"
          required
          maxLength={255}
          value={form.nombre_comercial}
          onChange={(event) => setField('nombre_comercial')(event.target.value)}
          error={mergedErrors.nombre_comercial}
          helper="Nombre con el que conocen tu bodega tus clientes."
        />
        <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
          <TextField
            label="RIF"
            name="rif"
            helper={RIF_HELP}
            maxLength={20}
            value={form.rif}
            onChange={(event) => setField('rif')(event.target.value)}
            error={mergedErrors.rif}
          />
          <TextField
            label="Razón social"
            name="razon_social"
            maxLength={255}
            value={form.razon_social}
            onChange={(event) => setField('razon_social')(event.target.value)}
            error={mergedErrors.razon_social}
            helper="Opcional. Nombre legal registrado."
          />
        </div>
        <TextField
          label="Dirección"
          name="direccion"
          autoComplete="street-address"
          maxLength={255}
          value={form.direccion}
          onChange={(event) => setField('direccion')(event.target.value)}
          error={mergedErrors.direccion}
        />
        <TextField
          label="Dirección fiscal"
          name="direccion_fiscal"
          maxLength={255}
          value={form.direccion_fiscal}
          onChange={(event) => setField('direccion_fiscal')(event.target.value)}
          error={mergedErrors.direccion_fiscal}
        />
        <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
          <TextField
            label="Teléfono"
            name="telefono"
            type="tel"
            autoComplete="tel"
            maxLength={50}
            value={form.telefono}
            onChange={(event) => setField('telefono')(event.target.value)}
            error={mergedErrors.telefono}
          />
          <SelectField
            label="Moneda principal"
            name="moneda"
            value={form.moneda}
            onChange={(event) => setField('moneda')(event.target.value)}
            error={mergedErrors.moneda}
            helper="Moneda base de tus precios."
          >
            {VALID_CURRENCIES.map((moneda) => (
              <option key={moneda} value={moneda}>
                {moneda === 'VES' ? 'Bolívares (VES)' : 'Dólares (USD)'}
              </option>
            ))}
          </SelectField>
        </div>

        <div className="flex items-center justify-end gap-3 border-t border-border-subtle pt-5">
          <button
            type="submit"
            disabled={isSaving || (config !== null && !isDirty)}
            aria-busy={isSaving}
            className="rounded-lg bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground transition-colors hover:bg-primary-deep disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isSaving ? 'Guardando…' : isCreateMode ? 'Guardar configuración' : 'Guardar cambios'}
          </button>
        </div>
      </form>
    </section>
  );
}
