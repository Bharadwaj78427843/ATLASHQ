import { useState } from "react";
import { request } from "@/lib/api";

export interface ExecutionResponse {
  execution_id: string;
  prompt?: string;
}

export interface ExecutionStatus {
  status: "pending" | "running" | "completed" | "failed";
  result?: string;
  error?: string;
}

export function useAgents(workspaceId: string) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const executeAgent = async (prompt: string, organizationId?: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await request<ExecutionResponse>('/ai/agents/execute', {
        method: 'POST',
        body: JSON.stringify({
          prompt,
          workspace_id: workspaceId,
          organization_id: organizationId
        })
      });
      return response;
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : "Failed to execute agent";
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const getStatus = async (executionId: string) => {
    try {
      const response = await request<ExecutionStatus>(`/ai/agents/status/${executionId}`);
      return response;
    } catch (err: unknown) {
      throw err;
    }
  };

  return {
    executeAgent,
    getStatus,
    loading,
    error,
    clearError: () => setError(null)
  };
}
