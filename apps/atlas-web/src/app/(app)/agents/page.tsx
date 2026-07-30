"use client";

import React, { useState, useEffect } from "react";
import { useActiveOrganization } from "@/contexts/OrganizationContext";
import { useWorkspaces } from "@/features/workspaces/hooks/useWorkspaces";
import { useAgents, ExecutionResponse, ExecutionStatus } from "@/features/ai/hooks/useAgents";
import { PageHeader } from "@/components/ui/PageHeader";
import { PageLayout } from "@/components/layout/PageLayout";
import { EmptyState } from "@/components/ui/EmptyState";
import { Button } from "@/components/ui/Button";
import { Bot, Loader2, Play } from "lucide-react";
import { SkeletonLoader } from "@/components/ui/SkeletonLoader";
import { ErrorState } from "@/components/ui/ErrorState";

export default function AgentsPage() {
  const { activeOrganization } = useActiveOrganization();
  const { data: workspacesData, loading: workspacesLoading } = useWorkspaces(activeOrganization?.id || "");
  const [activeWorkspaceId, setActiveWorkspaceId] = useState<string | null>(null);

  const [prompt, setPrompt] = useState("");
  const [execution, setExecution] = useState<ExecutionResponse | null>(null);
  const [executionStatus, setExecutionStatus] = useState<ExecutionStatus | null>(null);

  const currentWorkspaceId = activeWorkspaceId || (workspacesData?.items && workspacesData.items.length > 0 ? workspacesData.items[0].id : null);

  const { executeAgent, getStatus, loading, error, clearError } = useAgents(currentWorkspaceId || "");

  // Poll status if execution is active
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (execution?.execution_id && (!executionStatus || ["pending", "running"].includes(executionStatus.status))) {
      interval = setInterval(async () => {
        try {
          const status = await getStatus(execution.execution_id);
          setExecutionStatus(status);
        } catch (err) {
          console.error("Failed to get agent status", err);
        }
      }, 2000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [execution, executionStatus, getStatus]);

  const handleExecute = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim() || !activeWorkspaceId) return;

    try {
      const res = await executeAgent(prompt, activeOrganization?.id);
      setExecution(res);
      setExecutionStatus({ status: "pending" });
      setPrompt("");
    } catch {
      // Error handled by hook
    }
  };

  if (!activeOrganization) {
    return (
      <PageLayout>
        <PageHeader title="AI Agents" />
        <EmptyState
          icon={Bot}
          title="No Organization Selected"
          description="Please select or create an organization first to use agents."
        />
      </PageLayout>
    );
  }

  if (workspacesLoading) {
    return (
      <PageLayout>
        <PageHeader title="AI Agents" />
        <SkeletonLoader lines={5} />
      </PageLayout>
    );
  }

  if (!workspacesData || workspacesData.items.length === 0) {
    return (
      <PageLayout>
        <PageHeader title="AI Agents" />
        <EmptyState
          icon={Bot}
          title="No Workspace Available"
          description="You need a workspace to execute AI agents."
        />
      </PageLayout>
    );
  }

  return (
    <PageLayout maxWidth="3xl">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-2">AI Agents</h1>
          <p className="text-[var(--color-text-secondary)]">Run autonomous AI agents to perform complex tasks in your workspace.</p>
        </div>
        {workspacesData.items.length > 1 && (
          <select 
            value={activeWorkspaceId || ""} 
            onChange={(e) => setActiveWorkspaceId(e.target.value)}
            className="px-3 py-2 bg-[var(--color-background)] border border-[var(--color-border-subtle)] rounded-[var(--radius-md)] text-sm"
          >
            {workspacesData.items.map(ws => (
              <option key={ws.id} value={ws.id}>{ws.name}</option>
            ))}
          </select>
        )}
      </div>

      {error && <ErrorState error={error} onRetry={clearError} />}

      <form onSubmit={handleExecute} className="bg-[var(--color-panel)] border border-[var(--color-border-subtle)] rounded-[var(--radius-lg)] p-4 mb-8">
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Instruct the agent to perform a task... (e.g., 'Analyze the recent pull requests in the frontend repository')"
          className="w-full bg-transparent border-none text-[var(--color-text-primary)] placeholder-[var(--color-text-muted)] focus:outline-none resize-none min-h-[100px] mb-4 text-base"
        />
        <div className="flex justify-between items-center pt-4 border-t border-[var(--color-border-subtle)]">
          <span className="text-sm text-[var(--color-text-muted)]">Agents use context from your workspace knowledge base.</span>
          <Button 
            type="submit" 
            variant="primary" 
            disabled={!!(!prompt.trim() || loading || (executionStatus && ["pending", "running"].includes(executionStatus.status)))}
          >
            {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Play className="w-4 h-4 mr-2" />}
            Execute Agent
          </Button>
        </div>
      </form>

      {execution && (
        <div className="border border-[var(--color-border-subtle)] bg-[var(--color-panel)] rounded-[var(--radius-lg)] overflow-hidden">
          <div className="p-4 border-b border-[var(--color-border-subtle)] flex items-center justify-between bg-[rgba(255,255,255,0.02)]">
            <h3 className="font-semibold text-[var(--color-text-primary)] flex items-center gap-2">
              <Bot className="w-4 h-4 text-[var(--color-primary-base)]" />
              Agent Execution
            </h3>
            <span className="px-2 py-1 text-xs font-medium rounded-full bg-[rgba(255,255,255,0.1)] text-[var(--color-text-secondary)] capitalize">
              {executionStatus?.status || "Starting..."}
            </span>
          </div>
          
          <div className="p-6">
            <div className="mb-6">
              <h4 className="text-xs font-semibold text-[var(--color-text-muted)] uppercase tracking-wider mb-2">Prompt</h4>
              <p className="text-sm text-[var(--color-text-secondary)]">{execution.prompt || prompt}</p>
            </div>

            {executionStatus && (
              <div>
                <h4 className="text-xs font-semibold text-[var(--color-text-muted)] uppercase tracking-wider mb-3">Status</h4>
                
                {["pending", "running"].includes(executionStatus.status) && (
                  <div className="flex items-center gap-3 text-sm text-[var(--color-text-primary)] bg-[rgba(124,58,237,0.1)] p-4 rounded-[var(--radius-md)] border border-[rgba(124,58,237,0.2)]">
                    <Loader2 className="w-4 h-4 animate-spin text-[var(--color-primary-base)]" />
                    Agent is working...
                  </div>
                )}

                {executionStatus.status === "completed" && (
                  <div className="text-sm text-[var(--color-text-primary)] bg-[rgba(34,197,94,0.1)] p-4 rounded-[var(--radius-md)] border border-[rgba(34,197,94,0.2)]">
                    {executionStatus.result || "Task completed successfully."}
                  </div>
                )}
                
                {executionStatus.status === "failed" && (
                  <div className="text-sm text-red-500 bg-red-500/10 p-4 rounded-[var(--radius-md)] border border-red-500/20">
                    {executionStatus.error || "Agent execution failed."}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </PageLayout>
  );
}
