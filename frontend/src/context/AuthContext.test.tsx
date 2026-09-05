import { act, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { AuthProvider, useAuth } from './AuthContext';
import { TOKEN_STORAGE_KEY, USER_STORAGE_KEY } from '@/lib/apiClient';

const loginMock = vi.fn();
const logoutMock = vi.fn();

vi.mock('@/lib/apiClient', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/lib/apiClient')>();
  return {
    ...actual,
    authApi: {
      login: (...args: unknown[]) => loginMock(...args),
      logout: (...args: unknown[]) => logoutMock(...args),
    },
  };
});

type LoginFn = (username: string, password: string) => Promise<void>;

function SessionProbe({ onLogin }: { onLogin?: (fn: LoginFn) => void }) {
  const { isAuthenticated, user, login, logout } = useAuth();
  onLogin?.(login);
  return (
    <div>
      <span>{isAuthenticated ? `authenticated:${user?.username}` : 'anonymous'}</span>
      <button type="button" onClick={logout}>
        logout
      </button>
    </div>
  );
}

function renderWithProvider(onLogin?: (fn: LoginFn) => void) {
  return render(
    <AuthProvider>
      <SessionProbe onLogin={onLogin} />
    </AuthProvider>,
  );
}

describe('AuthContext', () => {
  it('restores a persisted session on mount', () => {
    localStorage.setItem(
      TOKEN_STORAGE_KEY,
      JSON.stringify({ accessToken: 'work.token', refreshToken: 'contractor.token' }),
    );
    localStorage.setItem(USER_STORAGE_KEY, JSON.stringify({ id: '1', username: 'admin' }));

    renderWithProvider();

    expect(screen.getByText('authenticated:admin')).toBeInTheDocument();
  });

  it('login stores dual tokens and updates session state', async () => {
    loginMock.mockResolvedValue({
      access_token: 'new.access',
      refresh_token: 'new.refresh',
    });
    let loginFn: LoginFn | undefined;
    renderWithProvider((fn) => {
      loginFn = fn;
    });

    expect(screen.getByText('anonymous')).toBeInTheDocument();
    await act(async () => {
      await loginFn!('admin', 'secreto');
    });

    await waitFor(() => expect(screen.getByText('authenticated:admin')).toBeInTheDocument());
    const stored = JSON.parse(localStorage.getItem(TOKEN_STORAGE_KEY) ?? '{}');
    expect(stored.accessToken).toBe('new.access');
    expect(stored.refreshToken).toBe('new.refresh');
    expect(loginMock).toHaveBeenCalledWith('admin', 'secreto');
  });

  it('logout revokes the contractor token on the server before clearing the session', async () => {
    logoutMock.mockResolvedValue(undefined);
    localStorage.setItem(
      TOKEN_STORAGE_KEY,
      JSON.stringify({ accessToken: 'work.token', refreshToken: 'contractor.token' }),
    );
    localStorage.setItem(USER_STORAGE_KEY, JSON.stringify({ id: '1', username: 'admin' }));
    const user = userEvent.setup();

    renderWithProvider();
    await user.click(screen.getByRole('button', { name: 'logout' }));

    await waitFor(() => expect(screen.getByText('anonymous')).toBeInTheDocument());
    expect(logoutMock).toHaveBeenCalledWith('contractor.token');
    expect(localStorage.getItem(TOKEN_STORAGE_KEY)).toBeNull();
    expect(localStorage.getItem(USER_STORAGE_KEY)).toBeNull();
  });

  it('logout clears the session even if the server revocation fails', async () => {
    logoutMock.mockRejectedValue(new Error('network down'));
    localStorage.setItem(
      TOKEN_STORAGE_KEY,
      JSON.stringify({ accessToken: 'work.token', refreshToken: 'contractor.token' }),
    );
    localStorage.setItem(USER_STORAGE_KEY, JSON.stringify({ id: '1', username: 'admin' }));
    const user = userEvent.setup();

    renderWithProvider();
    await user.click(screen.getByRole('button', { name: 'logout' }));

    await waitFor(() => expect(screen.getByText('anonymous')).toBeInTheDocument());
    expect(logoutMock).toHaveBeenCalledWith('contractor.token');
    expect(localStorage.getItem(TOKEN_STORAGE_KEY)).toBeNull();
    expect(localStorage.getItem(USER_STORAGE_KEY)).toBeNull();
  });
});
