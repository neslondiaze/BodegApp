import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios';
import type { LoginResponse, RefreshResponse } from '@/types/auth';

/**
 * API client for BodegApp backend (Nelson's FastAPI service).
 *
 * Dual-token architecture (req 0-2):
 * - Work token (access): attached as Bearer on every request via interceptor.
 * - Contractor token (refresh): used ONLY to obtain a new work token when the
 *   current one expires (HTTP 401). If the refresh also fails, the session is
 *   terminated via the onUnauthorized hook registered by AuthContext.
 */

export const TOKEN_STORAGE_KEY = 'bodegapp.tokens';
export const USER_STORAGE_KEY = 'bodegapp.user';

export const apiClient = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
});

type RetryConfig = InternalAxiosRequestConfig & { _isRetry?: boolean };

let getRefreshToken: () => string | null = () => null;
let onUnauthorized: () => void = () => {};

/** AuthContext registers how to read the contractor token and handle logout. */
export function configureAuthCallbacks(callbacks: {
  getRefreshToken: () => string | null;
  onUnauthorized: () => void;
}): void {
  getRefreshToken = callbacks.getRefreshToken;
  onUnauthorized = callbacks.onUnauthorized;
}

apiClient.interceptors.request.use((config) => {
  try {
    const raw = localStorage.getItem(TOKEN_STORAGE_KEY);
    if (raw) {
      const tokens = JSON.parse(raw) as { accessToken: string };
      if (tokens.accessToken) {
        config.headers.Authorization = `Bearer ${tokens.accessToken}`;
      }
    }
  } catch {
    /* corrupted storage — request proceeds without token */
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as RetryConfig | undefined;
    const isAuthEndpoint = original?.url?.includes('/auth/');
    const isRefreshCall = original?.url?.includes('/auth/refresh');

    if (
      error.response?.status !== 401 ||
      !original ||
      original._isRetry ||
      isAuthEndpoint
    ) {
      // Refresh calls that fail must log the user out.
      if (isRefreshCall) onUnauthorized();
      throw error;
    }

    original._isRetry = true;

    const contractorToken = getRefreshToken();
    if (!contractorToken) {
      onUnauthorized();
      throw error;
    }

    try {
      const { data } = await axios.post<RefreshResponse>('/api/v1/auth/refresh', {
        refresh_token: contractorToken,
      });
      const raw = localStorage.getItem(TOKEN_STORAGE_KEY);
      const tokens = raw ? (JSON.parse(raw) as { refreshToken: string }) : { refreshToken: '' };
      localStorage.setItem(
        TOKEN_STORAGE_KEY,
        JSON.stringify({ accessToken: data.access_token, refreshToken: tokens.refreshToken }),
      );
      original.headers.Authorization = `Bearer ${data.access_token}`;
      return apiClient(original);
    } catch {
      onUnauthorized();
      throw error;
    }
  },
);

export const authApi = {
  async login(username: string, password: string): Promise<LoginResponse> {
    const { data } = await apiClient.post<LoginResponse>('/auth/login', { username, password });
    return data;
  },
};
