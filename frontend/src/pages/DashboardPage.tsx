interface ModuleCard {
  id: string;
  title: string;
  description: string;
}

/** Placeholder module catalog (M-01..M-15 from docs/REQUERIMIENTOS.md §3). */
const MODULES: ModuleCard[] = [
  { id: 'M-01', title: 'Configuración de tienda', description: 'Datos de la tienda' },
  { id: 'M-02', title: 'Productos', description: 'Alta, baja, modificación y consulta' },
  { id: 'M-03', title: 'Proveedores', description: 'Gestión de proveedores' },
  { id: 'M-04', title: 'Código de barras', description: 'Escaneo EAN/UPC' },
  { id: 'M-05', title: 'Código QR', description: 'Escaneo de códigos QR' },
  { id: 'M-06', title: 'Alertas de mínimo', description: 'Aviso cuando el stock baja del mínimo' },
  { id: 'M-07', title: 'Reporte de compras', description: 'Lista de compras según stock y mínimos' },
  { id: 'M-08', title: 'Fiados', description: 'Ventas a crédito con abonos y fecha de pago' },
  { id: 'M-09', title: 'Historial de fiados', description: 'Fiados y abonos registrados' },
  { id: 'M-10', title: 'Scraping BCV', description: 'Captura de la tasa USD/Bs' },
  { id: 'M-11', title: 'Actualización dólar', description: 'Tasa BCV automática' },
  { id: 'M-12', title: 'Historial de tasa', description: 'Tasas capturadas en el tiempo' },
  { id: 'M-13', title: 'Configuración scraping', description: 'Días y horas de captura' },
  { id: 'M-14', title: 'Promociones WhatsApp', description: 'Diseño de promociones para envío' },
  { id: 'M-15', title: 'Peso electrónico', description: 'Balanza digital USB, RJ45 o serial' },
];

/** Dashboard placeholder showing the 15 functional modules. */
export function DashboardPage() {
  return (
    <section aria-labelledby="dashboard-title">
      <div className="mb-6">
        <h1
          id="dashboard-title"
          className="font-headline text-2xl font-bold tracking-tight text-content-base"
        >
          Panel
        </h1>
        <p className="mt-1 text-sm text-content-muted">
          Módulos disponibles en BodegApp. Cada tarjeta se activará cuando su fase esté en curso.
        </p>
      </div>
      <ul className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {MODULES.map((module) => (
          <li
            key={module.id}
            className="rounded-2xl border border-border-subtle bg-surface-card p-4 transition-transform hover:-translate-y-0.5"
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <h2 className="font-headline text-sm font-semibold text-content-base">
                  {module.title}
                </h2>
                <p className="mt-1 text-sm text-content-muted">{module.description}</p>
              </div>
              <span className="rounded-full bg-secondary/20 px-2 py-0.5 font-headline text-xs font-semibold text-content-base">
                {module.id}
              </span>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
