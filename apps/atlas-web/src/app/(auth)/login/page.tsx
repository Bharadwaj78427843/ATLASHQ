"use client";

/**
 * src/app/(auth)/login/page.tsx
 *
 * ATLAS-009 — Login page with form validation, loading states, and errors.
 */
import React, { useState, FormEvent } from "react";
import Link from "next/link";
import { Hexagon } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { ApiError } from "@/lib/api";
import { GlassPanel } from "@/components/ui/GlassPanel";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { AuthLayout } from "@/components/layout/AuthLayout";
import { Alert } from "@/components/ui/Alert";
import { FormField } from "@/components/ui/FormField";

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
    <AuthLayout>
      <GlassPanel className="w-full max-w-md p-8 relative z-10" glow>
        <div className="flex flex-col items-center mb-8">
          <div className="w-12 h-12 rounded-xl bg-[rgba(124,58,237,0.1)] flex items-center justify-center mb-4 border border-[rgba(124,58,237,0.3)]">
            <Hexagon className="w-6 h-6 text-[var(--color-primary-light)]" />
          </div>
          <h1 className="text-2xl font-bold text-center">Welcome back</h1>
          <p className="text-sm text-[var(--color-text-secondary)] mt-2">Sign in to your Atlas account</p>
        </div>

        {error && (
          <Alert variant="error" className="mb-6">
            {error}
          </Alert>
        )}

        <form onSubmit={handleSubmit} noValidate className="space-y-4">
          <FormField label="Email" htmlFor="login-email" required>
            <Input
              id="login-email"
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
              disabled={busy}
              className="w-full"
            />
          </FormField>

          <FormField label="Password" htmlFor="login-password" required>
            <Input
              id="login-password"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
              disabled={busy}
              className="w-full"
            />
          </FormField>

          <div className="pt-4">
            <Button
              id="login-submit"
              type="submit"
              variant="primary"
              className="w-full h-11 text-base"
              disabled={busy}
            >
              {busy ? <span className="spinner-ring" aria-label="Signing in…" /> : "Sign in"}
            </Button>
          </div>
        </form>

        <p className="text-center text-sm text-[var(--color-text-secondary)] mt-8">
          No account?{" "}
          <Link href="/register" className="text-[var(--color-primary-light)] hover:text-[var(--color-primary-base)] transition-colors font-medium">
            Create one
          </Link>
        </p>
      </GlassPanel>
    </AuthLayout>
  );
}
