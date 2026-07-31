"use client";

import React, { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Rocket, RefreshCw } from "lucide-react";
import { PageLayout } from "@/components/layout/PageLayout";
import { PageHeader } from "@/components/ui/PageHeader";
import { GlassPanel } from "@/components/ui/GlassPanel";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { SkeletonLoader } from "@/components/ui/SkeletonLoader";
import { useWorkspaceSelection } from "@/hooks/useWorkspaceSelection";
import { projectsApi } from "@/features/projects/api";
import { environmentsApi } from "@/features/environments/api";
import type { EnvironmentRead } from "@/features/environments/types";

type DeploymentRow = {
  projectId: string;
  projectName: string;
  environment: EnvironmentRead;
};

export default function DeploymentsPage() {
  const router = useRouter();
  const { activeOrganization, activeWorkspace } = useWorkspaceSelection();
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [rows, setRows] = useState<DeploymentRow[]>([]);

  const orgId = activeOrganization?.id || "";
  const workspaceId = activeWorkspace?.id || "";

  const fetchDeployments = async () => {
    if (!workspaceId) {
      setRows([]);
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const projects = await projectsApi.list(workspaceId, 0, 100);
      const allRows: DeploymentRow[] = [];

      for (const project of projects.items) {
        const environments = await environmentsApi.list(workspaceId, project.id, 0, 100);
        for (const environment of environments.items) {
          allRows.push({
            projectId: project.id,
            projectName: project.name,
            environment,
          });
        }
      }

      allRows.sort((a, b) => new Date(b.environment.updated_at).getTime() - new Date(a.environment.updated_at).getTime());
      setRows(allRows);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Failed to load deployments";
      setError(message);
      setRows([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void fetchDeployments();
  }, [workspaceId]);

  const byType = useMemo(() => {
    return rows.reduce<Record<string, number>>((acc, row) => {
      acc[row.environment.type] = (acc[row.environment.type] || 0) + 1;
      return acc;
    }, {});
  }, [rows]);

  return (
    <PageLayout>
      <PageHeader
        title="Deployments"
        subtitle="Environment and deployment targets across the active workspace."
      >
        <Button variant="secondary" className="gap-2" onClick={() => void fetchDeployments()} disabled={isLoading}>
          <RefreshCw className="w-4 h-4" />
          Refresh
        </Button>
      </PageHeader>

      {error ? <ErrorState title="Unable to load deployments" error={error} onRetry={() => void fetchDeployments()} /> : null}

      {isLoading ? (
        <GlassPanel className="p-6">
          <SkeletonLoader lines={7} />
        </GlassPanel>
      ) : null}

      {!isLoading && rows.length === 0 ? (
        <EmptyState
          icon={Rocket}
          title="No deployments found"
          description="Create a project and add environments to start deployment tracking."
          actionLabel="Go to Projects"
          onAction={() => {
            if (orgId && workspaceId) {
              router.push(`/organizations/${orgId}/workspaces/${workspaceId}/projects`);
            }
          }}
        />
      ) : null}

      {!isLoading && rows.length > 0 ? (
        <div className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(byType).map(([type, count]) => (
              <GlassPanel key={type} className="p-4">
                <p className="text-xs text-[var(--color-text-muted)] mb-1">{type}</p>
                <p className="text-xl font-semibold">{count}</p>
              </GlassPanel>
            ))}
          </div>

          <GlassPanel className="p-0 overflow-hidden">
            <div className="divide-y divide-[var(--color-border-subtle)]">
              {rows.map((row) => (
                <div key={row.environment.id} className="p-4 flex flex-wrap items-center justify-between gap-3 hover:bg-[rgba(255,255,255,0.02)]">
                  <div>
                    <p className="text-sm font-semibold text-[var(--color-text-primary)]">{row.environment.name}</p>
                    <p className="text-xs text-[var(--color-text-secondary)]">
                      Project: {row.projectName} • Type: {row.environment.type}
                    </p>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-xs uppercase text-[var(--color-text-muted)]">
                      {row.environment.is_active ? "Active" : "Inactive"}
                    </span>
                    <Link href={`/organizations/${orgId}/workspaces/${workspaceId}/projects/${row.projectId}/environments/${row.environment.id}`}>
                      <Button size="sm" variant="secondary">Open</Button>
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          </GlassPanel>
        </div>
      ) : null}
    </PageLayout>
  );
}
