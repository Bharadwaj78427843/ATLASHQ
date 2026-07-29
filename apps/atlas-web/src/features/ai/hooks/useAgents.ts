import { useState } from "react";
import { request } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";

export function useAgents(workspaceId: string) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const executeAgent = async (prompt: string, organizationId?: string) => {
    const token = getAccessToken();
    if (!token) throw new Error("Not authenticated");
    
    setLoading(true);
    setError(null);
    try {
      const response = await request<any>('/ai/agents/execute', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: JSON.stringify({
          prompt,
          workspace_id: workspaceId,
          organization_id: organizationId
        })
      });
      return response;
    } catch (err: any) {
      setError(err.message || "Failed to execute agent");
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const getStatus = async (executionId: string) => {
    const token = getAccessToken();
    if (!token) throw new Error("Not authenticated");
    
    try {
      const response = await request<any>(`/ai/agents/status/${executionId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return response;
    } catch (err: any) {
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
