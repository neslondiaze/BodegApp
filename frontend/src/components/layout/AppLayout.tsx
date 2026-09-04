import { Outlet, useLocation } from 'react-router-dom';
import { Link } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { useTheme } from '@/hooks/useTheme';

interface NavItem {
  label: string;
  href: string;
}

const NAV_ITEMS: NavItem[] = [
  { label: 'Panel', href: '/' },
  { label: 'Inventario', href: '/inventario' },
  { label: 'Fiados', href: '/fiados' },
  { label: 'Compras', href: '/compras' },
  { label: 'Configuración', href: '/configuracion' },
];

function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();
  const nextLabel = theme === 'dark' ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro';
  return (
    <button
      type="button"
      onClick={toggleTheme}
      aria-label={nextLabel}
      title={nextLabel}
      className="flex h-9 w-9 items-center justify-center rounded-lg border border-border-subtle bg-surface-card text-content-muted transition-colors hover:text-content-base"
    >
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        {theme === 'dark' ? (
          <circle cx="12" cy="12" r="4.5" stroke="currentColor" strokeWidth="1.8" />
        ) : (
          <path
            d="M21 12.8A8.5 8.5 0 1 1 11.2 3a6.8 6.8 0 0 0 9.8 9.8Z"
            stroke="currentColor"
            strokeWidth="1.8"
            strokeLinejoin="round"
          />
        )}
      </svg>
    </button>
  );
}

/** Sidebar navigation + topbar application shell with nested route outlet. */
export function AppLayout() {
  const { user, logout } = useAuth();
  const { pathname } = useLocation();
  const activeHref = NAV_ITEMS.find(
    (item) => item.href !== '/' && pathname.startsWith(item.href),
  )?.href;

  return (
    <div className="flex min-h-screen bg-surface">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-md focus:bg-secondary focus:px-3 focus:py-2 focus:font-medium focus:text-content-base"
      >
        Saltar al contenido principal
      </a>
      <aside className="hidden w-60 shrink-0 flex-col border-r border-border-subtle bg-surface-card md:flex">
        <div className="flex items-center gap-2 px-5 py-5">
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary font-headline text-lg font-bold text-primary-foreground">
            B
          </span>
          <span className="font-headline text-lg font-bold tracking-tight text-content-base">
            BodegApp
          </span>
        </div>
        <nav aria-label="Navegación principal" className="flex-1 space-y-1 px-3">
          {NAV_ITEMS.map((item) => {
            const isActive = item.href === activeHref;
            return (
              <Link
                key={item.href}
                to={item.href}
                aria-current={isActive ? 'page' : undefined}
                className={`block rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-primary/10 text-primary'
                    : 'text-content-muted hover:bg-primary/5 hover:text-content-base'
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
      </aside>
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-14 items-center justify-between border-b border-border-subtle bg-surface-card px-4">
          <span className="truncate text-sm text-content-muted md:hidden">BodegApp</span>
          <p className="hidden truncate text-sm text-content-muted md:block">
            {user?.storeName ?? user?.username ?? 'Sesión activa'}
          </p>
          <div className="flex items-center gap-3">
            <ThemeToggle />
            <button
              type="button"
              onClick={logout}
              className="rounded-lg border border-border-subtle px-3 py-2 text-sm font-medium text-content-muted transition-colors hover:border-primary hover:text-primary"
            >
              Salir
            </button>
          </div>
        </header>
        <main id="main-content" className="flex-1 overflow-y-auto p-4 md:p-6">
          <div className="mx-auto max-w-6xl">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
