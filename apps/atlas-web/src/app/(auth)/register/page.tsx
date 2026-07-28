"use client";

/**
 * src/app/(auth)/register/page.tsx
 *
 * ATLAS-009 — Registration page with validation, loading states, and errors.
 */
import React, { useState, FormEvent } from "react";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import { ApiError } from "@/lib/api";

export default function RegisterPage() {
  const { register, isLoading } = useAuth();
  const [form, setForm] = useState({
    email: "",
    username: "",
    password: "",
    first_name: "",
    last_name: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  function onChange(field: keyof typeof form) {
    return (e: React.ChangeEvent<HTMLInputElement>) =>
      setForm((prev) => ({ ...prev, [field]: e.target.value }));
  }

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);

    if (form.password.length < 8) {
      setError("Password must be at least 8 characters");
      return;
    }

    setSubmitting(true);
    try {
      await register({
        email: form.email,
        username: form.username,
        password: form.password,
        first_name: form.first_name || undefined,
        last_name: form.last_name || undefined,
      });
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Registration failed");
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

      <h1 className="auth-title">Create your account</h1>
      <p className="auth-subtitle">Start building on Atlas today</p>

      {error && (
        <div className="alert alert-error" role="alert">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} noValidate>
        <div className="form-row">
          <div className="form-group">
            <label className="form-label" htmlFor="reg-first-name">
              First name
            </label>
            <input
              id="reg-first-name"
              type="text"
              className="form-input"
              placeholder="Alice"
              value={form.first_name}
              onChange={onChange("first_name")}
              disabled={busy}
            />
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="reg-last-name">
              Last name
            </label>
            <input
              id="reg-last-name"
              type="text"
              className="form-input"
              placeholder="Smith"
              value={form.last_name}
              onChange={onChange("last_name")}
              disabled={busy}
            />
          </div>
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="reg-email">
            Email
          </label>
          <input
            id="reg-email"
            type="email"
            className="form-input"
            placeholder="you@example.com"
            value={form.email}
            onChange={onChange("email")}
            required
            autoComplete="email"
            disabled={busy}
          />
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="reg-username">
            Username
          </label>
          <input
            id="reg-username"
            type="text"
            className="form-input"
            placeholder="alice_atlas"
            value={form.username}
            onChange={onChange("username")}
            required
            minLength={3}
            maxLength={50}
            disabled={busy}
          />
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="reg-password">
            Password
          </label>
          <input
            id="reg-password"
            type="password"
            className="form-input"
            placeholder="At least 8 characters"
            value={form.password}
            onChange={onChange("password")}
            required
            minLength={8}
            autoComplete="new-password"
            disabled={busy}
          />
        </div>

        <button
          id="register-submit"
          type="submit"
          className="btn-primary"
          disabled={busy}
        >
          {busy ? (
            <span className="btn-spinner" aria-label="Creating account…" />
          ) : (
            "Create account"
          )}
        </button>
      </form>

      <p className="auth-footer">
        Already have an account?{" "}
        <Link href="/login" className="auth-link">
          Sign in
        </Link>
      </p>
    </>
  );
}
