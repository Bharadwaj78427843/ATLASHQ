"use client";

/**
 * src/contexts/AuthContext.tsx
 *
 * ATLAS-010 — React session management context.
 * Provides user state, login/logout helpers, and auto-login on mount.
 */
import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import { useRouter } from "next/navigation";
import { api, UserRead, LoginPayload, RegisterPayload, ApiError } from "@/lib/api";
import {
  getAccessToken,
  clearTokens,
  setTokens,
} from "@/lib/auth";

interface AuthState {
  user: UserRead | null;
  isLoading: boolean;
  error: string | null;
}

interface AuthContextValue extends AuthState {
  login: (payload: LoginPayload) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => void;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [state, setState] = useState<AuthState>({
    user: null,
    isLoading: true,
    error: null,
  });

  // ── Auto-login on mount ───────────────────────────────────────────────────
  useEffect(() => {
    const token = getAccessToken();
    if (!token) {
      setState((s) => ({ ...s, isLoading: false }));
      return;
    }
    api
      .me(token)
      .then((user) => setState({ user, isLoading: false, error: null }))
      .catch(() => {
        clearTokens();
        setState({ user: null, isLoading: false, error: null });
      });
  }, []);

  // ── Login ─────────────────────────────────────────────────────────────────
  const login = useCallback(async (payload: LoginPayload) => {
    setState((s) => ({ ...s, isLoading: true, error: null }));
    try {
      const tokens = await api.login(payload);
      setTokens(tokens.access_token, tokens.refresh_token);
      const user = await api.me(tokens.access_token);
      setState({ user, isLoading: false, error: null });
      router.push("/dashboard");
    } catch (err) {
      const msg = err instanceof ApiError ? err.detail : "Login failed";
      setState((s) => ({ ...s, isLoading: false, error: msg }));
      throw err;
    }
  }, [router]);

  // ── Register ──────────────────────────────────────────────────────────────
  const register = useCallback(async (payload: RegisterPayload) => {
    setState((s) => ({ ...s, isLoading: true, error: null }));
    try {
      await api.register(payload);
      // Auto-login after successful registration
      await login({ email: payload.email, password: payload.password });
    } catch (err) {
      const msg = err instanceof ApiError ? err.detail : "Registration failed";
      setState((s) => ({ ...s, isLoading: false, error: msg }));
      throw err;
    }
  }, [login]);

  // ── Logout ────────────────────────────────────────────────────────────────
  const logout = useCallback(() => {
    clearTokens();
    setState({ user: null, isLoading: false, error: null });
    router.push("/login");
  }, [router]);

  const clearError = useCallback(() => {
    setState((s) => ({ ...s, error: null }));
  }, []);

  return (
    <AuthContext.Provider value={{ ...state, login, register, logout, clearError }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside <AuthProvider>");
  return ctx;
}
