"use client";

import { useState, useCallback, useEffect } from "react";
import { EnvironmentService } from "../services";
import { EnvironmentList, EnvironmentRead, EnvironmentCreate, EnvironmentUpdate } from "../types";

export function useEnvironments(workspaceId: string, projectId: string) {
  const [data, setData] = useState<EnvironmentList | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchEnvironments = useCallback(async (skip = 0, limit = 50) => {
    if (!workspaceId || !projectId) return;
    try {
      setLoading(true);
      setError(null);
      const result = await EnvironmentService.getEnvironments(workspaceId, projectId, skip, limit);
      setData(result);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : "Failed to fetch environments";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [workspaceId, projectId]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchEnvironments();
  }, [fetchEnvironments]);

  const createEnvironment = async (payload: EnvironmentCreate) => {
    const result = await EnvironmentService.createEnvironment(workspaceId, projectId, payload);
    await fetchEnvironments();
    return result;
  };

  const deleteEnvironment = async (environmentId: string) => {
    await EnvironmentService.deleteEnvironment(workspaceId, projectId, environmentId);
    await fetchEnvironments();
  };

  return {
    data,
    loading,
    error,
    fetchEnvironments,
    createEnvironment,
    deleteEnvironment,
  };
}

export function useEnvironment(workspaceId: string, projectId: string, environmentId: string) {
  const [data, setData] = useState<EnvironmentRead | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchEnvironment = useCallback(async () => {
    if (!workspaceId || !projectId || !environmentId) return;
    try {
      setLoading(true);
      setError(null);
      const result = await EnvironmentService.getEnvironment(workspaceId, projectId, environmentId);
      setData(result);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : "Failed to fetch environment";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [workspaceId, projectId, environmentId]);

  useEffect(() => {
    if (workspaceId && projectId && environmentId) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      fetchEnvironment();
    }
  }, [fetchEnvironment, workspaceId, projectId, environmentId]);

  const updateEnvironment = async (payload: EnvironmentUpdate) => {
    const result = await EnvironmentService.updateEnvironment(workspaceId, projectId, environmentId, payload);
    setData(result);
    return result;
  };

  return {
    data,
    loading,
    error,
    fetchEnvironment,
    updateEnvironment,
  };
}
