"use client";

import { useState, useCallback, useEffect } from "react";
import { WorkspaceService } from "../services";
import { WorkspaceList, WorkspaceRead, WorkspaceCreate, WorkspaceUpdate } from "../types";

export function useWorkspaces(orgId: string) {
  const [data, setData] = useState<WorkspaceList | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchWorkspaces = useCallback(async (skip = 0, limit = 50) => {
    if (!orgId) return;
    try {
      setLoading(true);
      setError(null);
      const result = await WorkspaceService.getWorkspaces(orgId, skip, limit);
      setData(result);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : "Failed to fetch workspaces";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [orgId]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchWorkspaces();
  }, [fetchWorkspaces]);

  const createWorkspace = async (payload: WorkspaceCreate) => {
    const result = await WorkspaceService.createWorkspace(orgId, payload);
    await fetchWorkspaces();
    return result;
  };

  const deleteWorkspace = async (workspaceId: string) => {
    await WorkspaceService.deleteWorkspace(orgId, workspaceId);
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
    if (!orgId || !workspaceId) return;
    try {
      setLoading(true);
      setError(null);
      const result = await WorkspaceService.getWorkspace(orgId, workspaceId);
      setData(result);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : "Failed to fetch workspace";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [orgId, workspaceId]);

  useEffect(() => {
    if (orgId && workspaceId) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      fetchWorkspace();
    }
  }, [fetchWorkspace, orgId, workspaceId]);

  const updateWorkspace = async (payload: WorkspaceUpdate) => {
    const result = await WorkspaceService.updateWorkspace(orgId, workspaceId, payload);
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
