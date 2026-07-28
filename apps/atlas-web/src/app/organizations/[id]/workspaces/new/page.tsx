"use client";

import React, { useState, FormEvent, use } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useWorkspaces } from "@/hooks/useWorkspaces";

export default function NewWorkspacePage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const orgId = resolvedParams.id;
  const router = useRouter();
  
  const { createWorkspace } = useWorkspaces(orgId);
  const [form, setForm] = useState({ name: "", slug: "", description: "" });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      await createWorkspace(form);
      router.push(`/organizations/${orgId}`);
    } catch (err: any) {
      setError(err.message || "Failed to create workspace");
      setIsSubmitting(false);
    }
  };

  return (
    <div style={{ maxWidth: "600px", margin: "0 auto", paddingBottom: "40px" }}>
      <div style={{ marginBottom: "32px" }}>
        <Link href={`/organizations/${orgId}`} style={{ color: "var(--text-secondary)", textDecoration: "none", fontSize: "14px", display: "inline-block", marginBottom: "16px" }}>
          ← Back to Organization
        </Link>
        <h1 className="hero-title" style={{ fontSize: "28px", margin: 0 }}>Create Workspace</h1>
      </div>

      <div className="profile-card">
        {error && (
          <div className="alert alert-error" style={{ marginBottom: "24px" }}>
            {error}
          </div>
        )}
        <form onSubmit={handleSubmit} noValidate>
          <div className="form-group">
            <label className="form-label" htmlFor="ws-name">Workspace Name *</label>
            <input
              id="ws-name"
              type="text"
              className="form-input"
              value={form.name}
              onChange={(e) => {
                const name = e.target.value;
                const slug = name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
                setForm(f => ({ ...f, name, slug: f.slug || slug }));
              }}
              required
              disabled={isSubmitting}
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="ws-slug">URL Slug *</label>
            <input
              id="ws-slug"
              type="text"
              className="form-input"
              value={form.slug}
              onChange={(e) => setForm(f => ({ ...f, slug: e.target.value }))}
              required
              pattern="[a-z0-9\-]+"
              disabled={isSubmitting}
            />
            <p style={{ fontSize: "12px", color: "var(--text-secondary)", marginTop: "4px" }}>
              Only lowercase letters, numbers, and hyphens.
            </p>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="ws-desc">Description</label>
            <textarea
              id="ws-desc"
              className="form-input"
              value={form.description}
              onChange={(e) => setForm(f => ({ ...f, description: e.target.value }))}
              rows={3}
              style={{ resize: "vertical" }}
              disabled={isSubmitting}
            />
          </div>

          <div style={{ marginTop: "32px", display: "flex", justifyContent: "flex-end", gap: "12px" }}>
            <Link href={`/organizations/${orgId}`} className="btn-ghost" style={{ textDecoration: "none", lineHeight: "2.5" }}>
              Cancel
            </Link>
            <button type="submit" className="btn-primary" disabled={isSubmitting || !form.name || !form.slug}>
              {isSubmitting ? <span className="btn-spinner" /> : "Create Workspace"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
