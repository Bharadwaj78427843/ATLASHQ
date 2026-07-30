/**
 * src/lib/auth.ts
 *
 * ATLAS-010 — Token storage helpers.
 * Stores access + refresh tokens in localStorage (client-side only).
 */

const ACCESS_KEY = "atlas_access_token";
const REFRESH_KEY = "atlas_refresh_token";

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(ACCESS_KEY);
}

export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(REFRESH_KEY);
}

export function setTokens(accessToken: string, refreshToken: string): void {
  localStorage.setItem(ACCESS_KEY, accessToken);
  localStorage.setItem(REFRESH_KEY, refreshToken);
}

export function clearTokens(): void {
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

export function hasToken(): boolean {
  return Boolean(getAccessToken());
}
