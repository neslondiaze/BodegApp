export interface AuthTokens {
  /** Work token — short-lived, sent as Bearer on every API request. */
  accessToken: string;
  /** Contractor token — long-lived, used only to obtain new work tokens. */
  refreshToken: string;
}

export interface AuthUser {
  id: string;
  username: string;
  fullName?: string;
  storeName?: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
}

export interface RefreshResponse {
  access_token: string;
}

export interface MeResponse {
  id: string;
  username: string;
  full_name?: string;
  store_name?: string;
}
