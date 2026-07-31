"use client";

import React, { FormEvent, use, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { useOrganizationMembers } from "@/features/organizations";
import { useEnvironment } from "@/features/environments/hooks/useEnvironments";
import { EnvironmentService } from "@/features/environments/services";
import { ConfirmDialog } from "@/components/ui/ConfirmDialog";
import { Button } from "@/components/ui/Button";

export default function EnvironmentDetailsPage({
  params,
}: {
  params: Promise<{ id: string; workspaceId: string; projectId: string; environmentId: string }>;
}) {
  const resolved = use(params);
  const router = useRouter();
  const { user } = useAuth();

  const orgId = resolved.id;
  const workspaceId = resolved.workspaceId;
  const projectId = resolved.projectId;
  const environmentId = resolved.environmentId;

  const { data: members, fetchMembers } = useOrganizationMembers(orgId);
  const { data: environment, loading, error, fetchEnvironment, updateEnvironment } = useEnvironment(
    workspaceId,
    projectId,
    environmentId
  );

  const [isEditing, setIsEditing] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const [form, setForm] = useState<{ name: string; type: string; is_active: boolean }>({ name: "", type: "DEVELOPMENT", is_active: true });

  useEffect(() => {
    void fetchEnvironment();
    void fetchMembers();
  }, [fetchEnvironment, fetchMembers]);

  const currentMember = members?.items.find((member) => member.user_id === user?.id);
  const canManage = currentMember?.role === "OWNER" || currentMember?.role === "ADMIN";

  const openEdit = () => {
    if (!environment) return;
    setForm({ name: environment.name, type: environment.type, is_active: environment.is_active });
    setActionError(null);
    setIsEditing(true);
  };

  const handleSave = async (event: FormEvent) => {
    event.preventDefault();
    setIsSubmitting(true);
    setActionError(null);

    try {
      await updateEnvironment({
        name: form.name,
        type: form.type as any,
        is_active: form.is_active,
      });
      setIsEditing(false);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Failed to update environment";
      setActionError(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async () => {
    setIsSubmitting(true);
    setActionError(null);

    try {
      await EnvironmentService.deleteEnvironment(workspaceId, projectId, environmentId);
      router.push(`/organizations/${orgId}/workspaces/${workspaceId}/projects/${projectId}`);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Failed to delete environment";
      setActionError(message);
      setIsSubmitting(false);
      setShowDeleteDialog(false);
    }
  };

  if (loading && !environment) {
    return <div className="py-12 text-center"><span className="spinner-ring" /></div>;
  }

  if (error || !environment) {
    return <div className="alert alert-error">{error || "Environment not found"}</div>;
  }

  return (
    <div style={{ maxWidth: "720px", margin: "0 auto", paddingBottom: "40px" }}>
      <div style={{ marginBottom: "24px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <Link
            href={`/organizations/${orgId}/workspaces/${workspaceId}/projects/${projectId}`}
            style={{ color: "var(--text-secondary)", textDecoration: "none", fontSize: "14px", display: "inline-block", marginBottom: "12px" }}
          >
            ← Back to Project
          </Link>
          <h1 className="hero-title" style={{ fontSize: "28px", margin: 0 }}>{environment.name}</h1>
        </div>

        {canManage && !isEditing ? (
          <div style={{ display: "flex", gap: "10px" }}>
            <button className="btn-ghost" onClick={openEdit}>Edit Environment</button>
            <button
              className="btn-ghost"
              style={{ color: "var(--error)", borderColor: "rgba(239,68,68,0.3)" }}
              onClick={() => setShowDeleteDialog(true)}
            >
              Delete Environment
            </button>
          </div>
        ) : null}
      </div>

      {actionError ? <div className="alert alert-error">{actionError}</div> : null}

      <div className="profile-card">
        {isEditing ? (
          <form onSubmit={handleSave}>
            <h2 className="profile-card-title">Edit Environment</h2>

            <div className="form-group">
              <label className="form-label" htmlFor="environment-name">Name</label>
              <input
                id="environment-name"
                className="form-input"
                value={form.name}
                onChange={(event) => setForm((prev) => ({ ...prev, name: event.target.value }))}
                disabled={isSubmitting}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="environment-type">Type</label>
              <select
                id="environment-type"
                className="form-input"
                value={form.type}
                onChange={(event) => setForm((prev) => ({ ...prev, type: event.target.value }))}
                disabled={isSubmitting}
              >
                <option value="DEVELOPMENT">Development</option>
                <option value="PREVIEW">Preview</option>
                <option value="STAGING">Staging</option>
                <option value="PRODUCTION">Production</option>
              </select>
            </div>

            <div className="form-group" style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <input
                id="environment-active"
                type="checkbox"
                checked={form.is_active}
                onChange={(event) => setForm((prev) => ({ ...prev, is_active: event.target.checked }))}
                disabled={isSubmitting}
              />
              <label htmlFor="environment-active" className="form-label" style={{ margin: 0 }}>Active</label>
            </div>

            <div style={{ marginTop: "22px", display: "flex", justifyContent: "flex-end", gap: "10px" }}>
              <Button type="button" variant="ghost" onClick={() => setIsEditing(false)} disabled={isSubmitting}>Cancel</Button>
              <Button type="submit" variant="primary" disabled={isSubmitting || !form.name.trim()}>
                {isSubmitting ? <span className="spinner-ring" /> : "Save Changes"}
              </Button>
            </div>
          </form>
        ) : (
          <>
            <h2 className="profile-card-title">Environment Details</h2>
            <dl className="profile-grid">
              <dt>Type</dt>
              <dd>{environment.type}</dd>
              <dt>Status</dt>
              <dd>{environment.is_active ? "Active" : "Inactive"}</dd>
              <dt>Created</dt>
              <dd>{new Date(environment.created_at).toLocaleDateString()}</dd>
            </dl>
          </>
        )}
      </div>

      <ConfirmDialog
        isOpen={showDeleteDialog}
        title="Delete Environment"
        description={`Delete environment \"${environment.name}\"? This action cannot be undone.`}
        confirmLabel="Delete"
        cancelLabel="Cancel"
        isDestructive
        isLoading={isSubmitting}
        onCancel={() => setShowDeleteDialog(false)}
        onConfirm={() => void handleDelete()}
      />
    </div>
  );
}
