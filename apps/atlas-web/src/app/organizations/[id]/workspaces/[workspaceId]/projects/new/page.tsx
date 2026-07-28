"use client";

import React, { useState, FormEvent, use } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useProjects } from "@/hooks/useProjects";

export default function NewProjectPage({ params }: { params: Promise<{ id: string, workspaceId: string }> }) {
  const resolvedParams = use(params);
  const orgId = resolvedParams.id;
  const workspaceId = resolvedParams.workspaceId;
  const router = useRouter();
  
  const { createProject } = useProjects(workspaceId);
  const [form, setForm] = useState({ name: "", description: "" });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      await createProject(form);
      router.push(`/organizations/${orgId}/workspaces/${workspaceId}`);
    } catch (err: any) {
      setError(err.message || "Failed to create project");
      setIsSubmitting(false);
    }
  };

  return (
    <div style={{ maxWidth: "600px", margin: "0 auto", paddingBottom: "40px" }}>
      <div style={{ marginBottom: "32px" }}>
        <Link href={`/organizations/${orgId}/workspaces/${workspaceId}`} style={{ color: "var(--text-secondary)", textDecoration: "none", fontSize: "14px", display: "inline-block", marginBottom: "16px" }}>
          ← Back to Workspace
        </Link>
        <h1 className="hero-title" style={{ fontSize: "28px", margin: 0 }}>Create Project</h1>
      </div>

      <div className="profile-card">
        {error && (
          <div className="alert alert-error" style={{ marginBottom: "24px" }}>
            {error}
          </div>
        )}
        <form onSubmit={handleSubmit} noValidate>
          <div className="form-group">
            <label className="form-label" htmlFor="project-name">Project Name *</label>
            <input
              id="project-name"
              type="text"
              className="form-input"
              value={form.name}
              onChange={(e) => setForm(f => ({ ...f, name: e.target.value }))}
              required
              disabled={isSubmitting}
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="project-desc">Description</label>
            <textarea
              id="project-desc"
              className="form-input"
              value={form.description}
              onChange={(e) => setForm(f => ({ ...f, description: e.target.value }))}
              rows={3}
              style={{ resize: "vertical" }}
              disabled={isSubmitting}
            />
          </div>

          <div style={{ marginTop: "32px", display: "flex", justifyContent: "flex-end", gap: "12px" }}>
            <Link href={`/organizations/${orgId}/workspaces/${workspaceId}`} className="btn-ghost" style={{ textDecoration: "none", lineHeight: "2.5" }}>
              Cancel
            </Link>
            <button type="submit" className="btn-primary" disabled={isSubmitting || !form.name}>
              {isSubmitting ? <span className="btn-spinner" /> : "Create Project"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
