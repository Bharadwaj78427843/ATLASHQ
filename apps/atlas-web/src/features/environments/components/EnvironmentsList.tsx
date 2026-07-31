"use client";

import React, { useEffect } from "react";
import Link from "next/link";
import { useEnvironments } from "../hooks/useEnvironments";
import { useAuth } from "@/contexts/AuthContext";
import { useOrganizationMembers } from "@/features/organizations";
import { EnvironmentCard } from "./EnvironmentCard";
import { Button } from "@/components/ui/Button";

export function EnvironmentsList({ orgId, workspaceId, projectId }: { orgId: string, workspaceId: string, projectId: string }) {
  const { user } = useAuth();
  const { data: environments, loading, error, fetchEnvironments } = useEnvironments(workspaceId, projectId);
  const { data: members, fetchMembers } = useOrganizationMembers(orgId);

  useEffect(() => {
    fetchEnvironments();
    fetchMembers();
  }, [fetchEnvironments, fetchMembers]);

  const currentMember = members?.items.find(m => m.user_id === user?.id);
  const canManage = currentMember?.role === "OWNER" || currentMember?.role === "ADMIN";

  if (loading && !environments) {
    return <div className="py-12 text-center"><span className="spinner-ring" /></div>;
  }

  if (error) {
    return <div className="alert alert-error">{error}</div>;
  }

  return (
    <div className="mt-8">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold text-[var(--color-text-primary)]">Environments</h2>
        {canManage && (
          <Link href={`/organizations/${orgId}/workspaces/${workspaceId}/projects/${projectId}/environments/new`}>
            <Button variant="primary">New Environment</Button>
          </Link>
        )}
      </div>
      
      {environments?.items.length === 0 ? (
        <div className="text-center py-12 text-[var(--color-text-secondary)] bg-[rgba(255,255,255,0.02)] rounded-[var(--radius-lg)] border border-[var(--color-border-subtle)]">
          No environments found in this project.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {environments?.items.map((environment) => (
            <EnvironmentCard key={environment.id} organizationId={orgId} workspaceId={workspaceId} projectId={projectId} environment={environment} />
          ))}
        </div>
      )}
    </div>
  );
}
