"use client";

/**
 * src/app/(auth)/register/page.tsx
 *
 * ATLAS-009 — Registration page with validation, loading states, and errors.
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
    <AuthLayout>
      <GlassPanel className="w-full max-w-md p-8 relative z-10" glow>
        <div className="flex flex-col items-center mb-8">
          <div className="w-12 h-12 rounded-xl bg-[rgba(124,58,237,0.1)] flex items-center justify-center mb-4 border border-[rgba(124,58,237,0.3)]">
            <Hexagon className="w-6 h-6 text-[var(--color-primary-light)]" />
          </div>
          <h1 className="text-2xl font-bold text-center">Create your account</h1>
          <p className="text-sm text-[var(--color-text-secondary)] mt-2">Start building on Atlas today</p>
        </div>

        {error && (
          <Alert variant="error" className="mb-6">
            {error}
          </Alert>
        )}

        <form onSubmit={handleSubmit} noValidate className="space-y-4">
          <div className="flex gap-4">
            <FormField label="First name" htmlFor="reg-first-name" className="flex-1">
              <Input
                id="reg-first-name"
                type="text"
                placeholder="Alice"
                value={form.first_name}
                onChange={onChange("first_name")}
                disabled={busy}
                className="w-full"
              />
            </FormField>
            <FormField label="Last name" htmlFor="reg-last-name" className="flex-1">
              <Input
                id="reg-last-name"
                type="text"
                placeholder="Smith"
                value={form.last_name}
                onChange={onChange("last_name")}
                disabled={busy}
                className="w-full"
              />
            </FormField>
          </div>

          <FormField label="Email" htmlFor="reg-email" required>
            <Input
              id="reg-email"
              type="email"
              placeholder="you@example.com"
              value={form.email}
              onChange={onChange("email")}
              required
              autoComplete="email"
              disabled={busy}
              className="w-full"
            />
          </FormField>

          <FormField label="Username" htmlFor="reg-username" required>
            <Input
              id="reg-username"
              type="text"
              placeholder="alice_atlas"
              value={form.username}
              onChange={onChange("username")}
              required
              minLength={3}
              maxLength={50}
              disabled={busy}
              className="w-full"
            />
          </FormField>

          <FormField label="Password" htmlFor="reg-password" required>
            <Input
              id="reg-password"
              type="password"
              placeholder="At least 8 characters"
              value={form.password}
              onChange={onChange("password")}
              required
              minLength={8}
              autoComplete="new-password"
              disabled={busy}
              className="w-full"
            />
          </FormField>

          <div className="pt-4">
            <Button
              id="register-submit"
              type="submit"
              variant="primary"
              className="w-full h-11 text-base"
              disabled={busy}
            >
              {busy ? <span className="spinner-ring" aria-label="Creating account…" /> : "Create account"}
            </Button>
          </div>
        </form>

        <p className="text-center text-sm text-[var(--color-text-secondary)] mt-8">
          Already have an account?{" "}
          <Link href="/login" className="text-[var(--color-primary-light)] hover:text-[var(--color-primary-base)] transition-colors font-medium">
            Sign in
          </Link>
        </p>
      </GlassPanel>
    </AuthLayout>
  );
}
