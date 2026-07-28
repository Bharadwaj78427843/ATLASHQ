"use client";

import React, { useEffect } from "react";
import Link from "next/link";
import { useProjects } from "@/hooks/useProjects";
import { useAuth } from "@/contexts/AuthContext";
import { useOrganizationMembers } from "@/hooks/useOrganizationMembers";

export function ProjectsList({ orgId, workspaceId }: { orgId: string, workspaceId: string }) {
  const { user } = useAuth();
  const { data: projects, loading, error, fetchProjects } = useProjects(workspaceId);
  const { data: members } = useOrganizationMembers(orgId);

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  const currentMember = members?.items.find(m => m.user_id === user?.id);
  const canManage = currentMember?.role === "OWNER" || currentMember?.role === "ADMIN" || currentMember?.role === "MEMBER";

  if (loading && !projects) {
    return <div style={{ padding: "24px 0", textAlign: "center" }}><span className="spinner-ring" /></div>;
  }

  if (error) {
    return <div className="alert alert-error">{error}</div>;
  }

  return (
    <div className="profile-card" style={{ marginTop: "32px", padding: 0, overflow: "hidden" }}>
      <div style={{ padding: "20px 24px", borderBottom: "1px solid var(--border)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h2 className="profile-card-title" style={{ margin: 0, padding: 0, border: "none" }}>Projects</h2>
        {canManage && (
          <Link href={`/organizations/${orgId}/workspaces/${workspaceId}/projects/new`} className="btn-primary" style={{ padding: "6px 16px", fontSize: "14px", textDecoration: "none" }}>
            New Project
          </Link>
        )}
      </div>
      
      <div style={{ display: "flex", flexDirection: "column" }}>
        {projects?.items.map((project) => (
          <div key={project.id} style={{ padding: "16px 24px", borderBottom: "1px solid var(--border)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <span style={{ fontWeight: 500, fontSize: "16px", color: "var(--text)" }}>
                  {project.name}
                </span>
                {!project.is_active && <span className="badge badge-red">Inactive</span>}
              </div>
              <div style={{ color: "var(--text-secondary)", fontSize: "14px", marginTop: "4px" }}>
                {project.description || <span style={{ fontStyle: "italic" }}>No description</span>}
              </div>
            </div>
          </div>
        ))}
        
        {projects?.items.length === 0 && (
          <div style={{ padding: "32px", textAlign: "center", color: "var(--text-secondary)" }}>
            No projects found in this workspace.
          </div>
        )}
      </div>
    </div>
  );
}
