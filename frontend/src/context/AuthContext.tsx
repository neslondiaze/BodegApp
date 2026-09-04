import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from 'react';
import { authApi, configureAuthCallbacks, TOKEN_STORAGE_KEY, USER_STORAGE_KEY } from '@/lib/apiClient';
import type { AuthTokens, AuthUser } from '@/types/auth';

interface AuthContextValue {
  user: AuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

function readTokens(): AuthTokens | null {
  try {
    const raw = localStorage.getItem(TOKEN_STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as AuthTokens;
    if (!parsed.accessToken || !parsed.refreshToken) return null;
    return parsed;
  } catch {
    return null;
  }
}

function readUser(): AuthUser | null {
  try {
    const raw = localStorage.getItem(USER_STORAGE_KEY);
    return raw ? (JSON.parse(raw) as AuthUser) : null;
  } catch {
    return null;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(() => readUser());
  const [isLoading, setIsLoading] = useState(false);
  const sessionRef = useRef(0);

  const clearSession = useCallback(() => {
    sessionRef.current += 1; // invalidate any in-flight login attempt
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    localStorage.removeItem(USER_STORAGE_KEY);
    setUser(null);
  }, []);

  const logout = useCallback(() => {
    clearSession();
  }, [clearSession]);

  useEffect(() => {
    configureAuthCallbacks({
      getRefreshToken: () => readTokens()?.refreshToken ?? null,
      onUnauthorized: () => clearSession(),
    });
  }, [clearSession]);

  const login = useCallback(
    async (username: string, password: string) => {
      setIsLoading(true);
      const session = ++sessionRef.current;
      try {
        const response = await authApi.login(username, password);
        if (session !== sessionRef.current) return; // superseded by logout
        const tokens: AuthTokens = {
          accessToken: response.access_token,
          refreshToken: response.refresh_token,
        };
        const authUser: AuthUser = { id: '', username };
        localStorage.setItem(TOKEN_STORAGE_KEY, JSON.stringify(tokens));
        localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(authUser));
        setUser(authUser);
      } finally {
        if (session === sessionRef.current) setIsLoading(false);
      }
    },
    [],
  );

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated: user !== null,
      isLoading,
      login,
      logout,
    }),
    [user, isLoading, login, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
