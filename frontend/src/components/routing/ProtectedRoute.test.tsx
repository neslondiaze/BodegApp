import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import { AuthProvider } from '@/context/AuthContext';
import { ProtectedRoute } from './ProtectedRoute';
import { TOKEN_STORAGE_KEY, USER_STORAGE_KEY } from '@/lib/apiClient';

function ProtectedContent() {
  return <p>contenido protegido</p>;
}

function PublicContent() {
  return <p>página de login</p>;
}

function renderRoutes(initialEntry: string) {
  return render(
    <MemoryRouter initialEntries={[initialEntry]}>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<PublicContent />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <ProtectedContent />
              </ProtectedRoute>
            }
          />
        </Routes>
      </AuthProvider>
    </MemoryRouter>,
  );
}

describe('ProtectedRoute', () => {
  it('redirects unauthenticated visitors to /login', () => {
    renderRoutes('/');

    expect(screen.getByText('página de login')).toBeInTheDocument();
    expect(screen.queryByText('contenido protegido')).not.toBeInTheDocument();
  });

  it('renders protected content for authenticated sessions', () => {
    localStorage.setItem(
      TOKEN_STORAGE_KEY,
      JSON.stringify({ accessToken: 'work.token', refreshToken: 'contractor.token' }),
    );
    localStorage.setItem(USER_STORAGE_KEY, JSON.stringify({ id: '1', username: 'admin' }));

    renderRoutes('/');

    expect(screen.getByText('contenido protegido')).toBeInTheDocument();
    expect(screen.queryByText('página de login')).not.toBeInTheDocument();
  });
});
