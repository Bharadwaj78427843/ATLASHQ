"use client";

import React, { useEffect } from "react";
import Link from "next/link";
import { useProjects } from "../hooks/useProjects";
import { useAuth } from "@/contexts/AuthContext";
import { useOrganizationMembers } from "@/features/organizations";
import { ProjectCard } from "./ProjectCard";
import { Button } from "@/components/ui/Button";

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
    return <div className="py-12 text-center"><span className="spinner-ring" /></div>;
  }

  if (error) {
    return <div className="alert alert-error">{error}</div>;
  }

  return (
    <div className="mt-8">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold text-[var(--color-text-primary)]">Projects</h2>
        {canManage && (
          <Link href={`/organizations/${orgId}/workspaces/${workspaceId}/projects/new`}>
            <Button variant="primary">New Project</Button>
          </Link>
        )}
      </div>
      
      {projects?.items.length === 0 ? (
        <div className="text-center py-12 text-[var(--color-text-secondary)] bg-[rgba(255,255,255,0.02)] rounded-[var(--radius-lg)] border border-[var(--color-border-subtle)]">
          No projects found in this workspace.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {projects?.items.map((project) => (
            <ProjectCard key={project.id} organizationId={orgId} workspaceId={workspaceId} project={project} />
          ))}
        </div>
      )}
    </div>
  );
}
