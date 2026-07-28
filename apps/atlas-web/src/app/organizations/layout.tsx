"use client";

/**
 * src/app/organizations/layout.tsx
 *
 * ATLAS-011 — Organization domain layout.
 * Ensures the user is authenticated.
 */
import React, { useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";

export default function OrganizationsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, isLoading, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !user) {
      router.replace("/login");
    }
  }, [isLoading, user, router]);

  if (isLoading || !user) {
    return (
      <div className="dashboard-loading">
        <span className="spinner-ring" />
      </div>
    );
  }

  const initials = [user.first_name, user.last_name]
    .filter(Boolean)
    .map((n) => n![0].toUpperCase())
    .join("") || user.username[0].toUpperCase();

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="dashboard-logo">
          <Link href="/dashboard" className="flex items-center gap-2" style={{ display: "flex", alignItems: "center", gap: "10px", textDecoration: "none" }}>
            <span className="auth-logo-icon">⬡</span>
            <span className="auth-logo-text">Atlas</span>
          </Link>
          <div style={{ width: '1px', height: '24px', background: 'var(--border)', margin: '0 16px' }} />
          <Link href="/organizations" style={{ color: 'var(--text-secondary)', textDecoration: 'none', fontSize: '14px', fontWeight: 500 }}>
            Organizations
          </Link>
        </div>
        <div className="dashboard-header-actions">
          <div className="avatar">{initials}</div>
          <button id="logout-btn" className="btn-ghost" onClick={logout}>
            Sign out
          </button>
        </div>
      </header>

      <main className="dashboard-main">{children}</main>
    </div>
  );
}
