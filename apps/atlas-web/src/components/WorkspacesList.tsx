"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useWorkspaces } from "@/hooks/useWorkspaces";
import { useAuth } from "@/contexts/AuthContext";
import { useOrganizationMembers } from "@/hooks/useOrganizationMembers";

export function WorkspacesList({ orgId }: { orgId: string }) {
  const { user } = useAuth();
  const { data: workspaces, loading, error, fetchWorkspaces } = useWorkspaces(orgId);
  const { data: members } = useOrganizationMembers(orgId);

  useEffect(() => {
    fetchWorkspaces();
  }, [fetchWorkspaces]);

  const currentMember = members?.items.find(m => m.user_id === user?.id);
  const canManage = currentMember?.role === "OWNER" || currentMember?.role === "ADMIN";

  if (loading && !workspaces) {
    return <div style={{ padding: "24px 0", textAlign: "center" }}><span className="spinner-ring" /></div>;
  }

  if (error) {
    return <div className="alert alert-error">{error}</div>;
  }

  return (
    <div className="profile-card" style={{ marginTop: "32px", padding: 0, overflow: "hidden" }}>
      <div style={{ padding: "20px 24px", borderBottom: "1px solid var(--border)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h2 className="profile-card-title" style={{ margin: 0, padding: 0, border: "none" }}>Workspaces</h2>
        {canManage && (
          <Link href={`/organizations/${orgId}/workspaces/new`} className="btn-primary" style={{ padding: "6px 16px", fontSize: "14px", textDecoration: "none" }}>
            New Workspace
          </Link>
        )}
      </div>
      
      <div style={{ display: "flex", flexDirection: "column" }}>
        {workspaces?.items.map((workspace) => (
          <div key={workspace.id} style={{ padding: "16px 24px", borderBottom: "1px solid var(--border)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <Link href={`/organizations/${orgId}/workspaces/${workspace.id}`} style={{ fontWeight: 500, fontSize: "16px", color: "var(--text)", textDecoration: "none" }}>
                  {workspace.name}
                </Link>
                {!workspace.is_active && <span className="badge badge-red">Inactive</span>}
              </div>
              <div style={{ color: "var(--text-secondary)", fontSize: "14px", marginTop: "4px" }}>
                {workspace.description || <span style={{ fontStyle: "italic" }}>No description</span>}
              </div>
            </div>
            <div style={{ display: "flex", gap: "8px" }}>
              <span className="code-pill">{workspace.slug}</span>
            </div>
          </div>
        ))}
        
        {workspaces?.items.length === 0 && (
          <div style={{ padding: "32px", textAlign: "center", color: "var(--text-secondary)" }}>
            No workspaces found in this organization.
          </div>
        )}
      </div>
    </div>
  );
}
