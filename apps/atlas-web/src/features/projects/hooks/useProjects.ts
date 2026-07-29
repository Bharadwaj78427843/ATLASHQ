"use client";

import { useState, useCallback, useEffect } from "react";
import { ProjectService } from "../services";
import { ProjectList, ProjectRead, ProjectCreate, ProjectUpdate } from "../types";
import { getAccessToken } from "@/lib/auth";

export function useProjects(workspaceId: string) {
  const [data, setData] = useState<ProjectList | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchProjects = useCallback(async (skip = 0, limit = 50) => {
    const token = getAccessToken();
    if (!token || !workspaceId) return;
    try {
      setLoading(true);
      setError(null);
      const result = await ProjectService.getProjects(token, workspaceId, skip, limit);
      setData(result);
    } catch (err: any) {
      setError(err.message || "Failed to fetch projects");
    } finally {
      setLoading(false);
    }
  }, [workspaceId]);

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  const createProject = async (payload: ProjectCreate) => {
    const token = getAccessToken();
    if (!token) throw new Error("Not authenticated");
    const result = await ProjectService.createProject(token, workspaceId, payload);
    await fetchProjects();
    return result;
  };

  const deleteProject = async (projectId: string) => {
    const token = getAccessToken();
    if (!token) throw new Error("Not authenticated");
    await ProjectService.deleteProject(token, workspaceId, projectId);
    await fetchProjects();
  };

  return {
    data,
    loading,
    error,
    fetchProjects,
    createProject,
    deleteProject,
  };
}

export function useProject(workspaceId: string, projectId: string) {
  const [data, setData] = useState<ProjectRead | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchProject = useCallback(async () => {
    const token = getAccessToken();
    if (!token || !workspaceId || !projectId) return;
    try {
      setLoading(true);
      setError(null);
      const result = await ProjectService.getProject(token, workspaceId, projectId);
      setData(result);
    } catch (err: any) {
      setError(err.message || "Failed to fetch project");
    } finally {
      setLoading(false);
    }
  }, [workspaceId, projectId]);

  useEffect(() => {
    if (workspaceId && projectId) {
      fetchProject();
    }
  }, [fetchProject, workspaceId, projectId]);

  const updateProject = async (payload: ProjectUpdate) => {
    const token = getAccessToken();
    if (!token) throw new Error("Not authenticated");
    const result = await ProjectService.updateProject(token, workspaceId, projectId, payload);
    setData(result);
    return result;
  };

  return {
    data,
    loading,
    error,
    fetchProject,
    updateProject,
  };
}
