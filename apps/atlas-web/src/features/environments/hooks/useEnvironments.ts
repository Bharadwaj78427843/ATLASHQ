"use client";

import { useState, useCallback, useEffect } from "react";
import { EnvironmentService } from "../services";
import { EnvironmentList, EnvironmentRead, EnvironmentCreate, EnvironmentUpdate } from "../types";
import { getAccessToken } from "@/lib/auth";

export function useEnvironments(workspaceId: string, projectId: string) {
  const [data, setData] = useState<EnvironmentList | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchEnvironments = useCallback(async (skip = 0, limit = 50) => {
    const token = getAccessToken();
    if (!token || !workspaceId || !projectId) return;
    try {
      setLoading(true);
      setError(null);
      const result = await EnvironmentService.getEnvironments(token, workspaceId, projectId, skip, limit);
      setData(result);
    } catch (err: any) {
      setError(err.message || "Failed to fetch environments");
    } finally {
      setLoading(false);
    }
  }, [workspaceId, projectId]);

  useEffect(() => {
    fetchEnvironments();
  }, [fetchEnvironments]);

  const createEnvironment = async (payload: EnvironmentCreate) => {
    const token = getAccessToken();
    if (!token) throw new Error("Not authenticated");
    const result = await EnvironmentService.createEnvironment(token, workspaceId, projectId, payload);
    await fetchEnvironments();
    return result;
  };

  const deleteEnvironment = async (environmentId: string) => {
    const token = getAccessToken();
    if (!token) throw new Error("Not authenticated");
    await EnvironmentService.deleteEnvironment(token, workspaceId, projectId, environmentId);
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
    const token = getAccessToken();
    if (!token || !workspaceId || !projectId || !environmentId) return;
    try {
      setLoading(true);
      setError(null);
      const result = await EnvironmentService.getEnvironment(token, workspaceId, projectId, environmentId);
      setData(result);
    } catch (err: any) {
      setError(err.message || "Failed to fetch environment");
    } finally {
      setLoading(false);
    }
  }, [workspaceId, projectId, environmentId]);

  useEffect(() => {
    if (workspaceId && projectId && environmentId) {
      fetchEnvironment();
    }
  }, [fetchEnvironment, workspaceId, projectId, environmentId]);

  const updateEnvironment = async (payload: EnvironmentUpdate) => {
    const token = getAccessToken();
    if (!token) throw new Error("Not authenticated");
    const result = await EnvironmentService.updateEnvironment(token, workspaceId, projectId, environmentId, payload);
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
