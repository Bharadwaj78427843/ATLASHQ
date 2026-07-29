"use client";

import React, { useEffect } from "react";
import Link from "next/link";
import { useWorkspaces } from "../hooks/useWorkspaces";
import { useAuth } from "@/contexts/AuthContext";
import { useOrganizationMembers } from "@/features/organizations";
import { WorkspaceCard } from "./WorkspaceCard";
import { Button } from "@/components/ui/Button";

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
    return <div className="py-12 text-center"><span className="spinner-ring" /></div>;
  }

  if (error) {
    return <div className="alert alert-error">{error}</div>;
  }

  return (
    <div className="mt-8">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold text-[var(--color-text-primary)]">Workspaces</h2>
        {canManage && (
          <Link href={`/organizations/${orgId}/workspaces/new`}>
            <Button variant="primary">New Workspace</Button>
          </Link>
        )}
      </div>
      
      {workspaces?.items.length === 0 ? (
        <div className="text-center py-12 text-[var(--color-text-secondary)] bg-[rgba(255,255,255,0.02)] rounded-[var(--radius-lg)] border border-[var(--color-border-subtle)]">
          No workspaces found in this organization.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {workspaces?.items.map((workspace) => (
            <WorkspaceCard key={workspace.id} organizationId={orgId} workspace={workspace} />
          ))}
        </div>
      )}
    </div>
  );
}
