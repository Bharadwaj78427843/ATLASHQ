"use client";

/**
 * src/app/organizations/page.tsx
 *
 * ATLAS-011 — Organization List page.
 * Displays all active organizations.
 */
import React from "react";
import Link from "next/link";
import { useOrganizations } from "@/hooks/useOrganizations";

export default function OrganizationsListPage() {
  const { data, isLoading, error } = useOrganizations("all");

  return (
    <>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "32px" }}>
        <div>
          <h1 className="hero-title" style={{ fontSize: "32px", marginBottom: "8px" }}>Organizations</h1>
          <p className="hero-subtitle">Browse all active organizations on Atlas.</p>
        </div>
        <Link href="/organizations/new" className="btn-primary" style={{ width: "auto", textDecoration: "none" }}>
          + New Organization
        </Link>
      </div>

      {error && (
        <div className="alert alert-error" role="alert">
          {error}
        </div>
      )}

      {isLoading ? (
        <div style={{ display: "flex", justifyContent: "center", padding: "60px 0" }}>
          <span className="spinner-ring" />
        </div>
      ) : data?.items.length === 0 ? (
        <div className="profile-card" style={{ textAlign: "center", padding: "60px 20px" }}>
          <h3 style={{ fontSize: "18px", color: "var(--text-primary)", marginBottom: "8px", fontWeight: 600 }}>No organizations found</h3>
          <p style={{ color: "var(--text-secondary)", marginBottom: "24px" }}>Get started by creating your first organization.</p>
          <Link href="/organizations/new" className="btn-primary" style={{ display: "inline-flex", width: "auto", textDecoration: "none" }}>
            Create Organization
          </Link>
        </div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: "20px" }}>
          {data?.items.map((org) => (
            <Link href={`/organizations/${org.id}`} key={org.id} style={{ textDecoration: "none" }}>
              <div className="profile-card" style={{ padding: "24px", height: "100%", transition: "transform 0.2s, box-shadow 0.2s", cursor: "pointer" }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = "translateY(-4px)";
                  e.currentTarget.style.boxShadow = "var(--shadow-glow)";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = "translateY(0)";
                  e.currentTarget.style.boxShadow = "var(--shadow-card)";
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "16px" }}>
                  <div className="avatar" style={{ width: "40px", height: "40px", fontSize: "16px" }}>
                    {org.name.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <h3 style={{ color: "var(--text-primary)", fontWeight: 600, fontSize: "16px" }}>{org.name}</h3>
                    <code className="code-pill" style={{ fontSize: "11px" }}>{org.slug}</code>
                  </div>
                </div>
                {org.description && (
                  <p style={{ color: "var(--text-secondary)", fontSize: "13px", display: "-webkit-box", WebkitLineClamp: 2, WebkitBoxOrient: "vertical", overflow: "hidden" }}>
                    {org.description}
                  </p>
                )}
                <div style={{ marginTop: "20px", display: "flex", gap: "8px" }}>
                  {org.website && (
                    <span className="badge badge-blue">Website</span>
                  )}
                  <span className="badge badge-green">Active</span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </>
  );
}
