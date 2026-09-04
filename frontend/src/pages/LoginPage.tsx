import { useState, type FormEvent } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';

interface LoginLocationState {
  from?: string;
}

/** Public login page — Spanish UI copy for Venezuelan end users. */
export function LoginPage() {
  const { login, isLoading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError('');
    try {
      await login(username, password);
      const from = (location.state as LoginLocationState | null)?.from ?? '/';
      navigate(from, { replace: true });
    } catch {
      setError('Usuario o contraseña incorrectos. Verificá tus datos e intentá de nuevo.');
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-surface px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <span className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-primary font-headline text-2xl font-bold text-primary-foreground">
            B
          </span>
          <h1 className="font-headline text-2xl font-bold tracking-tight text-content-base">
            BodegApp
          </h1>
          <p className="mt-1 text-sm text-content-muted">
            Ingresá para gestionar el inventario de tu bodega
          </p>
        </div>
        <form
          onSubmit={handleSubmit}
          className="space-y-4 rounded-2xl border border-border-subtle bg-surface-card p-6 shadow-sm"
          noValidate
        >
          {error && (
            <p role="alert" className="rounded-lg bg-primary/10 px-3 py-2 text-sm text-primary">
              {error}
            </p>
          )}
          <div>
            <label
              htmlFor="username"
              className="mb-1.5 block text-sm font-medium text-content-base"
            >
              Usuario
            </label>
            <input
              id="username"
              name="username"
              type="text"
              autoComplete="username"
              required
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              className="w-full rounded-lg border border-border-subtle bg-surface px-3 py-2 text-sm text-content-base placeholder:text-content-muted focus:border-primary focus:outline-none"
              placeholder="ej: admin"
            />
          </div>
          <div>
            <label
              htmlFor="password"
              className="mb-1.5 block text-sm font-medium text-content-base"
            >
              Contraseña
            </label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              className="w-full rounded-lg border border-border-subtle bg-surface px-3 py-2 text-sm text-content-base placeholder:text-content-muted focus:border-primary focus:outline-none"
              placeholder="Tu contraseña"
            />
          </div>
          <button
            type="submit"
            disabled={isLoading || username.trim() === '' || password === ''}
            className="w-full rounded-lg bg-primary px-3 py-2.5 text-sm font-semibold text-primary-foreground transition-colors hover:bg-primary-deep disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isLoading ? 'Ingresando…' : 'Ingresar'}
          </button>
          <p className="text-center text-xs text-content-muted">
            ¿Problemas para entrar? Contactá al administrador de tu tienda.
          </p>
        </form>
        <p className="mt-6 text-center text-xs text-content-muted">
          BodegApp — sistema de inventario para bodegas
        </p>
        <div className="mt-2 text-center">
          <Link to="/" className="text-xs text-content-muted underline hover:text-primary">
            Volver al panel
          </Link>
        </div>
      </div>
    </div>
  );
}
