import { useState, useCallback } from "react";
import { workspacesApi, WorkspaceList, WorkspaceRead, WorkspaceCreate, WorkspaceUpdate } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";

export function useWorkspaces(orgId: string) {
  const [data, setData] = useState<WorkspaceList | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchWorkspaces = useCallback(async (skip = 0, limit = 50) => {
    const token = getAccessToken();
    if (!token || !orgId) return;
    try {
      setLoading(true);
      setError(null);
      const result = await workspacesApi.list(token, orgId, skip, limit);
      setData(result);
    } catch (err: any) {
      setError(err.message || "Failed to fetch workspaces");
    } finally {
      setLoading(false);
    }
  }, [orgId]);

  const createWorkspace = async (payload: WorkspaceCreate) => {
    const token = getAccessToken();
    if (!token) throw new Error("Not authenticated");
    const result = await workspacesApi.create(token, orgId, payload);
    await fetchWorkspaces();
    return result;
  };

  const deleteWorkspace = async (workspaceId: string) => {
    const token = getAccessToken();
    if (!token) throw new Error("Not authenticated");
    await workspacesApi.delete(token, orgId, workspaceId);
    await fetchWorkspaces();
  };

  return {
    data,
    loading,
    error,
    fetchWorkspaces,
    createWorkspace,
    deleteWorkspace,
  };
}

export function useWorkspace(orgId: string, workspaceId: string) {
  const [data, setData] = useState<WorkspaceRead | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchWorkspace = useCallback(async () => {
    const token = getAccessToken();
    if (!token || !orgId || !workspaceId) return;
    try {
      setLoading(true);
      setError(null);
      const result = await workspacesApi.get(token, orgId, workspaceId);
      setData(result);
    } catch (err: any) {
      setError(err.message || "Failed to fetch workspace");
    } finally {
      setLoading(false);
    }
  }, [orgId, workspaceId]);

  const updateWorkspace = async (payload: WorkspaceUpdate) => {
    const token = getAccessToken();
    if (!token) throw new Error("Not authenticated");
    const result = await workspacesApi.update(token, orgId, workspaceId, payload);
    setData(result);
    return result;
  };

  return {
    data,
    loading,
    error,
    fetchWorkspace,
    updateWorkspace,
  };
}
