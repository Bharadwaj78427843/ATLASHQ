"use client";

import { useState, useCallback, useEffect } from "react";
import { WorkspaceService } from "../services";
import { WorkspaceList, WorkspaceRead, WorkspaceCreate, WorkspaceUpdate } from "../types";
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
      const result = await WorkspaceService.getWorkspaces(token, orgId, skip, limit);
      setData(result);
    } catch (err: any) {
      setError(err.message || "Failed to fetch workspaces");
    } finally {
      setLoading(false);
    }
  }, [orgId]);

  useEffect(() => {
    fetchWorkspaces();
  }, [fetchWorkspaces]);

  const createWorkspace = async (payload: WorkspaceCreate) => {
    const token = getAccessToken();
    if (!token) throw new Error("Not authenticated");
    const result = await WorkspaceService.createWorkspace(token, orgId, payload);
    await fetchWorkspaces();
    return result;
  };

  const deleteWorkspace = async (workspaceId: string) => {
    const token = getAccessToken();
    if (!token) throw new Error("Not authenticated");
    await WorkspaceService.deleteWorkspace(token, orgId, workspaceId);
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
      const result = await WorkspaceService.getWorkspace(token, orgId, workspaceId);
      setData(result);
    } catch (err: any) {
      setError(err.message || "Failed to fetch workspace");
    } finally {
      setLoading(false);
    }
  }, [orgId, workspaceId]);

  useEffect(() => {
    if (orgId && workspaceId) {
      fetchWorkspace();
    }
  }, [fetchWorkspace, orgId, workspaceId]);

  const updateWorkspace = async (payload: WorkspaceUpdate) => {
    const token = getAccessToken();
    if (!token) throw new Error("Not authenticated");
    const result = await WorkspaceService.updateWorkspace(token, orgId, workspaceId, payload);
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
