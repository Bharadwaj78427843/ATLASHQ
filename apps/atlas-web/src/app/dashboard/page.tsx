"use client";

/**
 * src/app/dashboard/page.tsx
 *
 * ATLAS-010 — Protected dashboard.
 * Redirects unauthenticated users to /login.
 * Shows the current user's profile from GET /auth/me.
 */
import React, { useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";

export default function DashboardPage() {
  const { user, isLoading, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !user) {
      router.replace("/login");
    }
  }, [isLoading, user, router]);

  if (isLoading) {
    return (
      <div className="dashboard-loading">
        <span className="spinner-ring" />
        <p>Loading…</p>
      </div>
    );
  }

  if (!user) return null;

  const initials = [user.first_name, user.last_name]
    .filter(Boolean)
    .map((n) => n![0].toUpperCase())
    .join("") || user.username[0].toUpperCase();

  const displayName =
    [user.first_name, user.last_name].filter(Boolean).join(" ") ||
    user.username;

  return (
    <div className="dashboard">
      {/* ── Header ───────────────────────────────────────────────── */}
      <header className="dashboard-header">
        <div className="dashboard-logo">
          <span className="auth-logo-icon">⬡</span>
          <span className="auth-logo-text">Atlas</span>
        </div>
        <div className="dashboard-header-actions">
          <div className="avatar">{initials}</div>
          <button
            id="logout-btn"
            className="btn-ghost"
            onClick={logout}
          >
            Sign out
          </button>
        </div>
      </header>

      {/* ── Hero ─────────────────────────────────────────────────── */}
      <main className="dashboard-main">
        <div className="dashboard-hero">
          <div className="hero-badge">Authenticated</div>
          <h1 className="hero-title">
            Welcome, <span className="hero-name">{displayName}</span>
          </h1>
          <p className="hero-subtitle" style={{ marginBottom: "24px" }}>
            Your session is active and verified via{" "}
            <code className="code-pill">GET /auth/me</code>
          </p>
          <Link href="/organizations" className="btn-primary" style={{ display: "inline-flex", width: "auto", textDecoration: "none", fontSize: "15px", padding: "12px 24px" }}>
            View Organizations →
          </Link>
        </div>

        {/* ── User card ────────────────────────────────────────── */}
        <section className="profile-card">
          <h2 className="profile-card-title">Session Details</h2>
          <dl className="profile-grid">
            <dt>ID</dt>
            <dd>
              <code className="code-pill">{user.id}</code>
            </dd>

            <dt>Email</dt>
            <dd>{user.email}</dd>

            <dt>Username</dt>
            <dd>@{user.username}</dd>

            <dt>Status</dt>
            <dd className="status-row">
              <span className={`badge ${user.is_active ? "badge-green" : "badge-red"}`}>
                {user.is_active ? "Active" : "Inactive"}
              </span>
              <span className={`badge ${user.is_verified ? "badge-blue" : "badge-gray"}`}>
                {user.is_verified ? "Verified" : "Unverified"}
              </span>
            </dd>

            <dt>Member since</dt>
            <dd>{new Date(user.created_at).toLocaleDateString()}</dd>
          </dl>
        </section>
      </main>
    </div>
  );
}
