"use client";

/**
 * src/app/organizations/[id]/page.tsx
 *
 * ATLAS-011 — Organization Details & Edit page.
 * Includes a delete confirmation dialog.
 */
import React, { useState, FormEvent, use } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useOrganization } from "@/features/organizations";
import { useAuth } from "@/contexts/AuthContext";
import { ApiError } from "@/lib/api";
import { WorkspacesList } from "@/features/workspaces";

export default function OrganizationDetailsPage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const router = useRouter();
  const { user } = useAuth();
  const { data: org, isLoading, error: fetchError, update, remove } = useOrganization(resolvedParams.id);

  const [isEditing, setIsEditing] = useState(false);
  const [form, setForm] = useState({ name: "", description: "", website: "" });
  const [editError, setEditError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  const isOwner = user?.id === org?.owner_id;

  function handleEditStart() {
    if (!org) return;
    setForm({
      name: org.name,
      description: org.description || "",
      website: org.website || "",
    });
    setEditError(null);
    setIsEditing(true);
  }

  async function handleEditSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setEditError(null);
    setIsSubmitting(true);

    try {
      await update({
        name: form.name,
        description: form.description || undefined,
        website: form.website || undefined,
      });
      setIsEditing(false);
    } catch (err) {
      setEditError(err instanceof ApiError ? err.detail : "Failed to update organization");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleDelete() {
    setIsSubmitting(true);
    try {
      await remove();
      router.push("/organizations");
    } catch (err) {
      setEditError(err instanceof ApiError ? err.detail : "Failed to delete organization");
      setIsSubmitting(false);
      setShowDeleteModal(false);
    }
  }

  if (isLoading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", padding: "60px 0" }}>
        <span className="spinner-ring" />
      </div>
    );
  }

  if (fetchError || !org) {
    return (
      <div className="alert alert-error" style={{ maxWidth: "600px", margin: "0 auto" }}>
        {fetchError || "Organization not found."}
      </div>
    );
  }

  return (
    <div style={{ maxWidth: "700px", margin: "0 auto" }}>
      <div style={{ marginBottom: "32px", display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <Link href="/organizations" style={{ color: "var(--text-secondary)", textDecoration: "none", fontSize: "14px", display: "inline-block", marginBottom: "16px" }}>
            ← Back to Organizations
          </Link>
          <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
            <div className="avatar" style={{ width: "56px", height: "56px", fontSize: "24px" }}>
              {org.name.charAt(0).toUpperCase()}
            </div>
            <div>
              <h1 className="hero-title" style={{ fontSize: "28px", margin: 0 }}>{org.name}</h1>
              <div style={{ display: "flex", gap: "8px", marginTop: "8px" }}>
                <code className="code-pill">{org.slug}</code>
                {!org.is_active && <span className="badge badge-red">Inactive</span>}
              </div>
            </div>
          </div>
        </div>

        {org.is_active && !isEditing && (
          <div style={{ display: "flex", gap: "12px", marginTop: "32px" }}>
            <Link href={`/organizations/${org.id}/members`} className="btn-ghost" style={{ textDecoration: 'none' }}>
              Manage Members
            </Link>
            {isOwner && (
              <>
                <button className="btn-ghost" onClick={handleEditStart}>Edit Details</button>
                <button 
                  className="btn-ghost" 
                  style={{ color: "var(--error)", borderColor: "rgba(239,68,68,0.3)" }}
                  onClick={() => setShowDeleteModal(true)}
                >
                  Delete
                </button>
              </>
            )}
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
            <h2 className="profile-card-title">Edit Organization</h2>
            
            <div className="form-group">
              <label className="form-label" htmlFor="edit-name">Name</label>
              <input
                id="edit-name"
                type="text"
                className="form-input"
                value={form.name}
                onChange={(e) => setForm(f => ({ ...f, name: e.target.value }))}
                required
                maxLength={120}
                disabled={isSubmitting}
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="edit-website">Website URL</label>
              <input
                id="edit-website"
                type="url"
                className="form-input"
                value={form.website}
                onChange={(e) => setForm(f => ({ ...f, website: e.target.value }))}
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
            <h2 className="profile-card-title">Organization Details</h2>
            <dl className="profile-grid">
              <dt>Description</dt>
              <dd>{org.description || <span style={{ color: "var(--text-muted)" }}>None provided</span>}</dd>
              
              <dt>Website</dt>
              <dd>
                {org.website ? (
                  <a href={org.website} target="_blank" rel="noreferrer" style={{ color: "var(--brand-from)", textDecoration: "none" }}>
                    {org.website}
                  </a>
                ) : <span style={{ color: "var(--text-muted)" }}>None provided</span>}
              </dd>
              
              <dt>Created</dt>
              <dd>{new Date(org.created_at).toLocaleDateString()}</dd>
              
              <dt>Role</dt>
              <dd>
                {isOwner ? <span className="badge badge-blue">Owner</span> : <span className="badge badge-gray">Member</span>}
              </dd>
            </dl>
          </>
        )}
      </div>

      <WorkspacesList orgId={org.id} />

      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div style={{
          position: "fixed", inset: 0, zIndex: 100, display: "flex", alignItems: "center", justifyContent: "center",
          background: "rgba(0,0,0,0.6)", backdropFilter: "blur(4px)"
        }}>
          <div className="auth-card" style={{ maxWidth: "400px" }}>
            <h2 className="auth-title" style={{ fontSize: "20px" }}>Delete Organization?</h2>
            <p className="auth-subtitle" style={{ marginBottom: "24px" }}>
              Are you sure you want to delete <strong>{org.name}</strong>? This action will deactivate the organization.
            </p>
            <div style={{ display: "flex", gap: "12px" }}>
              <button className="btn-ghost" style={{ flex: 1 }} onClick={() => setShowDeleteModal(false)} disabled={isSubmitting}>
                Cancel
              </button>
              <button 
                className="btn-primary" 
                style={{ flex: 1, background: "var(--error)", color: "white" }} 
                onClick={handleDelete}
                disabled={isSubmitting}
              >
                {isSubmitting ? <span className="btn-spinner" /> : "Delete"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
