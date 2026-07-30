"use client";

import React, { useState, FormEvent, use } from "react";

import Link from "next/link";
import { useWorkspace } from "@/features/workspaces";
import { useAuth } from "@/contexts/AuthContext";
import { useOrganizationMembers } from "@/features/organizations";
import { ProjectsList } from "@/features/projects";

export default function WorkspaceDetailsPage({ params }: { params: Promise<{ id: string, workspaceId: string }> }) {
  const resolvedParams = use(params);
  const orgId = resolvedParams.id;
  const workspaceId = resolvedParams.workspaceId;


  const { user } = useAuth();
  const { data: members } = useOrganizationMembers(orgId);
  const { data: workspace, loading, error, fetchWorkspace, updateWorkspace } = useWorkspace(orgId, workspaceId);

  const [isEditing, setIsEditing] = useState(false);
  const [form, setForm] = useState({ name: "", description: "" });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [editError, setEditError] = useState<string | null>(null);

  React.useEffect(() => {
    fetchWorkspace();
  }, [fetchWorkspace]);

  const currentMember = members?.items.find(m => m.user_id === user?.id);
  const canManage = currentMember?.role === "OWNER" || currentMember?.role === "ADMIN";

  function handleEditStart() {
    if (!workspace) return;
    setForm({
      name: workspace.name,
      description: workspace.description || "",
    });
    setEditError(null);
    setIsEditing(true);
  }

  async function handleEditSubmit(e: FormEvent) {
    e.preventDefault();
    setIsSubmitting(true);
    setEditError(null);

    try {
      await updateWorkspace({
        name: form.name,
        description: form.description || undefined,
      });
      setIsEditing(false);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : "Failed to update workspace";
      setEditError(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  }

  if (loading && !workspace) {
    return <div style={{ display: "flex", justifyContent: "center", padding: "60px 0" }}><span className="spinner-ring" /></div>;
  }

  if (error || !workspace) {
    return <div className="alert alert-error">{error || "Workspace not found"}</div>;
  }

  return (
    <div style={{ maxWidth: "700px", margin: "0 auto", paddingBottom: "40px" }}>
      <div style={{ marginBottom: "32px", display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <Link href={`/organizations/${orgId}`} style={{ color: "var(--text-secondary)", textDecoration: "none", fontSize: "14px", display: "inline-block", marginBottom: "16px" }}>
            ← Back to Organization
          </Link>
          <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
            <div className="avatar" style={{ width: "56px", height: "56px", fontSize: "24px" }}>
              {workspace.name.charAt(0).toUpperCase()}
            </div>
            <div>
              <h1 className="hero-title" style={{ fontSize: "28px", margin: 0 }}>{workspace.name}</h1>
              <div style={{ display: "flex", gap: "8px", marginTop: "8px" }}>
                <code className="code-pill">{workspace.slug}</code>
                {!workspace.is_active && <span className="badge badge-red">Inactive</span>}
              </div>
            </div>
          </div>
        </div>

        {canManage && workspace.is_active && !isEditing && (
          <div style={{ display: "flex", gap: "12px", marginTop: "32px" }}>
            <button className="btn-ghost" onClick={handleEditStart}>Edit Workspace</button>
          </div>
        )}
      </div>

      {editError && (
        <div className="alert alert-error" role="alert">
          {editError}
        </div>
      )}

      <div className="profile-card">
        {isEditing ? (
          <form onSubmit={handleEditSubmit} noValidate>
            <h2 className="profile-card-title">Edit Workspace</h2>
            
            <div className="form-group">
              <label className="form-label" htmlFor="edit-name">Name</label>
              <input
                id="edit-name"
                type="text"
                className="form-input"
                value={form.name}
                onChange={(e) => setForm(f => ({ ...f, name: e.target.value }))}
                required
                disabled={isSubmitting}
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="edit-desc">Description</label>
              <textarea
                id="edit-desc"
                className="form-input"
                value={form.description}
                onChange={(e) => setForm(f => ({ ...f, description: e.target.value }))}
                rows={4}
                style={{ resize: "vertical" }}
                disabled={isSubmitting}
              />
            </div>

            <div style={{ marginTop: "24px", display: "flex", justifyContent: "flex-end", gap: "12px" }}>
              <button type="button" className="btn-ghost" onClick={() => setIsEditing(false)} disabled={isSubmitting}>
                Cancel
              </button>
              <button type="submit" className="btn-primary" style={{ width: "auto" }} disabled={isSubmitting || !form.name}>
                {isSubmitting ? <span className="btn-spinner" /> : "Save Changes"}
              </button>
            </div>
          </form>
        ) : (
          <>
            <h2 className="profile-card-title">Workspace Details</h2>
            <dl className="profile-grid">
              <dt>Description</dt>
              <dd>{workspace.description || <span style={{ color: "var(--text-muted)" }}>None provided</span>}</dd>
              
              <dt>Created</dt>
              <dd>{new Date(workspace.created_at).toLocaleDateString()}</dd>
            </dl>
          </>
        )}
      </div>

      <ProjectsList orgId={orgId} workspaceId={workspaceId} />
    </div>
  );
}
