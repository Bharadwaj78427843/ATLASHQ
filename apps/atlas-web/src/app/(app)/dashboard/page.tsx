"use client";

import React, { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  AlertCircle,
  Bot,
  Folder,
  GitBranch,
  Rocket,
  Search,
  UploadCloud,
  Plus,
  Activity,
  FileText,
  Shield,
} from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { useWorkspaceSelection } from "@/hooks/useWorkspaceSelection";
import { MetricCard } from "@/components/ui/MetricCard";
import { GlassPanel } from "@/components/ui/GlassPanel";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { SkeletonLoader } from "@/components/ui/SkeletonLoader";
import { aiApi } from "@/features/ai";
import { projectsApi } from "@/features/projects/api";
import { knowledgeApi } from "@/lib/api";
import { environmentsApi } from "@/features/environments/api";

type DashboardStats = {
  projectCount: number;
  repositoryCount: number;
  sourceCount: number;
  deploymentCount: number;
  agentCount: number;
  openIssueCount: number;
  recentActivity: Array<{ title: string; sub: string; time: string; status: "success" | "error" | "info" }>;
  repoHealth: {
    readyRate: number;
    failureRate: number;
    freshnessRate: number;
    overall: number;
  };
  timeline: Array<{ name: string; status: string; time: string }>;
};

function relativeTime(iso: string): string {
  const time = new Date(iso).getTime();
  if (Number.isNaN(time)) {
    return "unknown";
  }

  const diffMs = Date.now() - time;
  const diffMin = Math.floor(diffMs / 60000);

  if (diffMin < 1) return "just now";
  if (diffMin < 60) return `${diffMin}m ago`;
  const diffHr = Math.floor(diffMin / 60);
  if (diffHr < 24) return `${diffHr}h ago`;
  return `${Math.floor(diffHr / 24)}d ago`;
}

function clampPercent(value: number): number {
  if (!Number.isFinite(value)) return 0;
  return Math.max(0, Math.min(100, Math.round(value)));
}

function DashboardSkeleton() {
  return (
    <div className="space-y-6">
      <GlassPanel className="p-6">
        <SkeletonLoader lines={3} />
      </GlassPanel>
      <div className="grid grid-cols-1 md:grid-cols-3 xl:grid-cols-6 gap-4">
        {Array.from({ length: 6 }).map((_, index) => (
          <GlassPanel key={index} className="p-4">
            <SkeletonLoader lines={2} />
          </GlassPanel>
        ))}
      </div>
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <GlassPanel className="p-5"><SkeletonLoader lines={6} /></GlassPanel>
        <GlassPanel className="p-5"><SkeletonLoader lines={6} /></GlassPanel>
        <GlassPanel className="p-5"><SkeletonLoader lines={6} /></GlassPanel>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const { user, isLoading: authLoading } = useAuth();
  const router = useRouter();
  const { activeOrganization, activeWorkspace, isLoading: workspaceLoading } = useWorkspaceSelection();

  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isLoadingStats, setIsLoadingStats] = useState(true);
  const [statsError, setStatsError] = useState<string | null>(null);

  const workspaceId = activeWorkspace?.id || "";

  useEffect(() => {
    if (!authLoading && !user) {
      router.replace("/login");
    }
  }, [authLoading, user, router]);

  const loadDashboard = useCallback(async () => {
    if (!workspaceId) {
      setStats(null);
      setIsLoadingStats(false);
      return;
    }

    try {
      setStatsError(null);
      setIsLoadingStats(true);

      const projects = await projectsApi.list(workspaceId, 0, 100);
      const sources = await knowledgeApi.listSources(workspaceId);

      const repositories = sources.filter((source) => source.source_type.toLowerCase() === "repository");
      const nonRepositorySources = sources.filter((source) => source.source_type.toLowerCase() !== "repository");

      const jobsBySource = await Promise.all(sources.map((source) => knowledgeApi.listJobs(source.id)));
      const allJobs = jobsBySource.flat();

      const providersResult = await aiApi.getProviders().catch(() => ({ providers: [] }));
      const activeProviderCount = providersResult.providers.filter((provider) => provider.is_active).length;

      const deploymentBatches = await Promise.all(
        projects.items.map((project) =>
          environmentsApi.list(workspaceId, project.id, 0, 100).catch(() => ({ items: [], total: 0, skip: 0, limit: 100 }))
        )
      );
      const deploymentCount = deploymentBatches.reduce((acc, batch) => acc + batch.items.length, 0);

      const failedRepos = repositories.filter((repo) => repo.status.toLowerCase() === "failed").length;
      const readyRepos = repositories.filter((repo) => repo.status.toLowerCase() === "ready").length;
      const recentlySynced = repositories.filter((repo) => {
        const metadata = repo.metadata_json as { last_sync?: string } | null;
        if (!metadata?.last_sync) {
          return false;
        }
        const ms = Date.now() - new Date(metadata.last_sync).getTime();
        return ms >= 0 && ms <= 7 * 24 * 60 * 60 * 1000;
      }).length;

      const repoTotal = repositories.length;
      const readyRate = repoTotal > 0 ? (readyRepos / repoTotal) * 100 : 0;
      const failureRate = repoTotal > 0 ? (failedRepos / repoTotal) * 100 : 0;
      const freshnessRate = repoTotal > 0 ? (recentlySynced / repoTotal) * 100 : 0;
      const overall = repoTotal > 0 ? (readyRate * 0.5 + freshnessRate * 0.35 + (100 - failureRate) * 0.15) : 0;

      const recentActivity: DashboardStats["recentActivity"] = [
        ...projects.items.slice(0, 3).map((project) => ({
          title: "Project updated",
          sub: project.name,
          time: relativeTime(project.updated_at),
          status: "success" as const,
        })),
        ...sources.slice(0, 3).map((source) => ({
          title: source.source_type.toLowerCase() === "repository" ? "Repository connected" : "Knowledge source added",
          sub: source.name,
          time: relativeTime(source.updated_at),
          status: source.status.toLowerCase() === "failed" ? "error" as const : "info" as const,
        })),
      ]
        .sort((a, b) => {
          const aTime = a.time === "just now" ? 0 : 1;
          const bTime = b.time === "just now" ? 0 : 1;
          return aTime - bTime;
        })
        .slice(0, 6);

      const timeline = allJobs
        .slice()
        .sort((a, b) => {
          const aTime = new Date(a.started_at || 0).getTime();
          const bTime = new Date(b.started_at || 0).getTime();
          return bTime - aTime;
        })
        .slice(0, 5)
        .map((job) => ({
          name: "Index job",
          status: job.status,
          time: relativeTime(job.started_at || job.completed_at || new Date().toISOString()),
        }));

      setStats({
        projectCount: projects.total,
        repositoryCount: repositories.length,
        sourceCount: nonRepositorySources.length,
        deploymentCount,
        agentCount: activeProviderCount,
        openIssueCount: failedRepos + allJobs.filter((job) => job.status.toLowerCase() === "failed").length,
        recentActivity,
        repoHealth: {
          readyRate: clampPercent(readyRate),
          failureRate: clampPercent(failureRate),
          freshnessRate: clampPercent(freshnessRate),
          overall: clampPercent(overall),
        },
        timeline,
      });
    } catch (err: unknown) {
      setStatsError(err instanceof Error ? err.message : "Failed to load dashboard data.");
      setStats(null);
    } finally {
      setIsLoadingStats(false);
    }
  }, [workspaceId]);

  useEffect(() => {
    let mounted = true;
    if (mounted) {
      loadDashboard().catch(console.error);
    }
    return () => { mounted = false; };
  }, [loadDashboard]);

  const greeting = useMemo(() => {
    const hour = new Date().getHours();
    if (hour < 12) return "Good morning";
    if (hour < 18) return "Good afternoon";
    return "Good evening";
  }, []);

  if (authLoading || !user) {
    return (
      <div className="h-screen flex items-center justify-center bg-[var(--color-background)]">
        <span className="spinner-ring" />
      </div>
    );
  }

  const displayName = user.first_name || user.username;

  return (
    <div className="p-8 space-y-6">
      <GlassPanel className="p-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold mb-2 tracking-tight">
              {greeting}, <span className="text-gradient">{displayName}</span>
            </h1>
            <p className="text-[var(--color-text-secondary)] text-sm">Atlas dashboard is showing live workspace activity and readiness.</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <span className="px-2.5 py-1 rounded-[var(--radius-sm)] border border-[rgba(124,58,237,0.3)] bg-[rgba(124,58,237,0.1)] text-[var(--color-primary-light)] text-[10px] font-semibold uppercase tracking-wider">
              Organization: {activeOrganization?.name || "Not selected"}
            </span>
            <span className="px-2.5 py-1 rounded-[var(--radius-sm)] border border-[rgba(34,197,94,0.3)] bg-[rgba(34,197,94,0.1)] text-[var(--color-accent-green)] text-[10px] font-semibold uppercase tracking-wider">
              Workspace: {activeWorkspace?.name || "Not selected"}
            </span>
          </div>
        </div>

        <div className="mt-5 grid grid-cols-2 md:grid-cols-5 gap-3">
          <Link href={workspaceId ? `/organizations/${activeOrganization?.id}/workspaces/${workspaceId}/projects/new` : "/organizations"}>
            <Button className="w-full gap-2" variant="secondary"><Plus className="w-4 h-4" />New Project</Button>
          </Link>
          <Link href={workspaceId ? `/organizations/${activeOrganization?.id}/workspaces/${workspaceId}/knowledge/upload` : "/knowledge"}>
            <Button className="w-full gap-2" variant="secondary"><UploadCloud className="w-4 h-4" />Upload Knowledge</Button>
          </Link>
          <Link href={workspaceId ? `/organizations/${activeOrganization?.id}/workspaces/${workspaceId}/knowledge/repositories` : "/repositories"}>
            <Button className="w-full gap-2" variant="secondary"><GitBranch className="w-4 h-4" />Connect Repository</Button>
          </Link>
          <Link href={workspaceId ? `/organizations/${activeOrganization?.id}/workspaces/${workspaceId}/projects` : "/projects"}>
            <Button className="w-full gap-2" variant="secondary"><Rocket className="w-4 h-4" />New Deployment</Button>
          </Link>
          <Link href="/dashboard">
            <Button className="w-full gap-2" variant="primary"><Bot className="w-4 h-4" />Ask Atlas</Button>
          </Link>
        </div>
      </GlassPanel>

      {workspaceLoading || isLoadingStats ? <DashboardSkeleton /> : null}

      {!workspaceLoading && !isLoadingStats && !activeWorkspace ? (
        <EmptyState
          icon={Folder}
          title="No workspace selected"
          description="Create or select a workspace to unlock project, repository, and knowledge insights."
          actionLabel="Go to Organizations"
          onAction={() => router.push("/organizations")}
        />
      ) : null}

      {statsError ? <ErrorState title="Dashboard unavailable" error={statsError} onRetry={() => void loadDashboard()} /> : null}

      {stats && !statsError ? (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 xl:grid-cols-6 gap-4">
            <MetricCard title="Projects" value={String(stats.projectCount)} icon={<Folder className="w-4 h-4" />} />
            <MetricCard title="Repositories" value={String(stats.repositoryCount)} icon={<GitBranch className="w-4 h-4" />} />
            <MetricCard title="Knowledge Sources" value={String(stats.sourceCount)} icon={<FileText className="w-4 h-4" />} />
            <MetricCard title="Deployments" value={String(stats.deploymentCount)} icon={<Rocket className="w-4 h-4" />} />
            <MetricCard title="Agents" value={String(stats.agentCount)} icon={<Bot className="w-4 h-4" />} />
            <MetricCard title="Open Issues" value={String(stats.openIssueCount)} icon={<AlertCircle className="w-4 h-4" />} />
          </div>

          <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
            <GlassPanel className="p-5">
              <h3 className="text-sm font-semibold mb-4 text-[var(--color-text-primary)]">Recent Activity</h3>
              {stats.recentActivity.length === 0 ? (
                <p className="text-sm text-[var(--color-text-secondary)]">No recent activity yet.</p>
              ) : (
                <div className="space-y-3">
                  {stats.recentActivity.map((activity, index) => (
                    <div key={`${activity.title}-${index}`} className="flex items-start gap-3">
                      <span className="w-2 h-2 mt-1.5 rounded-full bg-[var(--color-primary-base)]" />
                      <div className="min-w-0 flex-1">
                        <p className="text-sm text-[var(--color-text-primary)] truncate">{activity.title}</p>
                        <p className="text-xs text-[var(--color-text-secondary)]">{activity.sub}</p>
                      </div>
                      <span className="text-xs text-[var(--color-text-muted)]">{activity.time}</span>
                    </div>
                  ))}
                </div>
              )}
            </GlassPanel>

            <GlassPanel className="p-5">
              <h3 className="text-sm font-semibold mb-4 text-[var(--color-text-primary)]">Deployment Timeline</h3>
              {stats.timeline.length === 0 ? (
                <p className="text-sm text-[var(--color-text-secondary)]">No deployment timeline entries yet.</p>
              ) : (
                <div className="space-y-3">
                  {stats.timeline.map((item, index) => (
                    <div key={`${item.name}-${index}`} className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Activity className="w-4 h-4 text-[var(--color-primary-light)]" />
                        <div>
                          <p className="text-sm text-[var(--color-text-primary)]">{item.name}</p>
                          <p className="text-xs text-[var(--color-text-muted)]">{item.time}</p>
                        </div>
                      </div>
                      <span className="text-xs uppercase text-[var(--color-text-secondary)]">{item.status}</span>
                    </div>
                  ))}
                </div>
              )}
            </GlassPanel>

            <GlassPanel className="p-5">
              <h3 className="text-sm font-semibold mb-4 text-[var(--color-text-primary)]">Repository Health</h3>

              <div className="mb-4">
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-[var(--color-text-secondary)]">Overall Health</span>
                  <span className="text-[var(--color-text-primary)] font-semibold">{stats.repoHealth.overall}%</span>
                </div>
                <div className="h-2 rounded bg-[rgba(255,255,255,0.05)] overflow-hidden">
                  <div className="h-full bg-[var(--color-accent-green)]" style={{ width: `${stats.repoHealth.overall}%` }} />
                </div>
              </div>

              <div className="space-y-3 text-xs">
                <div>
                  <div className="flex justify-between mb-1"><span>Ready Rate</span><span>{stats.repoHealth.readyRate}%</span></div>
                  <div className="h-1.5 rounded bg-[rgba(255,255,255,0.05)] overflow-hidden">
                    <div className="h-full bg-[var(--color-accent-green)]" style={{ width: `${stats.repoHealth.readyRate}%` }} />
                  </div>
                </div>
                <div>
                  <div className="flex justify-between mb-1"><span>Freshness</span><span>{stats.repoHealth.freshnessRate}%</span></div>
                  <div className="h-1.5 rounded bg-[rgba(255,255,255,0.05)] overflow-hidden">
                    <div className="h-full bg-[var(--color-accent-blue)]" style={{ width: `${stats.repoHealth.freshnessRate}%` }} />
                  </div>
                </div>
                <div>
                  <div className="flex justify-between mb-1"><span>Failure Rate</span><span>{stats.repoHealth.failureRate}%</span></div>
                  <div className="h-1.5 rounded bg-[rgba(255,255,255,0.05)] overflow-hidden">
                    <div className="h-full bg-[var(--color-accent-red)]" style={{ width: `${stats.repoHealth.failureRate}%` }} />
                  </div>
                </div>
              </div>

              <div className="mt-4 flex justify-end">
                <Link href={workspaceId ? `/organizations/${activeOrganization?.id}/workspaces/${workspaceId}/knowledge/repositories` : "/repositories"}>
                  <Button size="sm" variant="secondary" className="gap-2">
                    <Shield className="w-3.5 h-3.5" /> View Repositories
                  </Button>
                </Link>
              </div>
            </GlassPanel>
          </div>

          {stats.projectCount === 0 && stats.repositoryCount === 0 && stats.sourceCount === 0 ? (
            <EmptyState
              icon={Folder}
              title="Your workspace is ready"
              description="Create your first project, upload knowledge, or connect a repository to start building with AtlasHQ."
              actionLabel="Create Project"
              onAction={() => router.push(`/organizations/${activeOrganization?.id}/workspaces/${workspaceId}/projects/new`)}
            />
          ) : null}
        </>
      ) : null}
    </div>
  );
}
