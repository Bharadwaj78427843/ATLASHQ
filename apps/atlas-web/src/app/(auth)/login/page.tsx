"use client";

/**
 * src/app/(auth)/login/page.tsx
 *
 * ATLAS-009 — Login page with form validation, loading states, and errors.
 */
import React, { useState, FormEvent } from "react";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import { ApiError } from "@/lib/api";

export default function LoginPage() {
  const { login, isLoading } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await login({ email, password });
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Something went wrong");
    } finally {
      setSubmitting(false);
    }
  }

  const busy = submitting || isLoading;

  return (
    <>
      <div className="auth-logo">
        <span className="auth-logo-icon">⬡</span>
        <span className="auth-logo-text">Atlas</span>
      </div>

      <h1 className="auth-title">Welcome back</h1>
      <p className="auth-subtitle">Sign in to your Atlas account</p>

      {error && (
        <div className="alert alert-error" role="alert">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} noValidate>
        <div className="form-group">
          <label className="form-label" htmlFor="login-email">
            Email
          </label>
          <input
            id="login-email"
            type="email"
            className="form-input"
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            autoComplete="email"
            disabled={busy}
          />
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="login-password">
            Password
          </label>
          <input
            id="login-password"
            type="password"
            className="form-input"
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete="current-password"
            disabled={busy}
          />
        </div>

        <button
          id="login-submit"
          type="submit"
          className="btn-primary"
          disabled={busy}
        >
          {busy ? (
            <span className="btn-spinner" aria-label="Signing in…" />
          ) : (
            "Sign in"
          )}
        </button>
      </form>

      <p className="auth-footer">
        No account?{" "}
        <Link href="/register" className="auth-link">
          Create one
        </Link>
      </p>
    </>
  );
}
