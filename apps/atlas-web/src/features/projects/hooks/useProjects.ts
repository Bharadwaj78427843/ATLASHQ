"use client";

import { useState, useCallback, useEffect } from "react";
import { ProjectService } from "../services";
import { ProjectList, ProjectRead, ProjectCreate, ProjectUpdate } from "../types";

export function useProjects(workspaceId: string) {
  const [data, setData] = useState<ProjectList | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchProjects = useCallback(async (skip = 0, limit = 50) => {
    if (!workspaceId) return;
    try {
      setLoading(true);
      setError(null);
      const result = await ProjectService.getProjects(workspaceId, skip, limit);
      setData(result);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : "Failed to fetch projects";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [workspaceId]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchProjects();
  }, [fetchProjects]);

  const createProject = async (payload: ProjectCreate) => {
    const result = await ProjectService.createProject(workspaceId, payload);
    await fetchProjects();
    return result;
  };

  const deleteProject = async (projectId: string) => {
    await ProjectService.deleteProject(workspaceId, projectId);
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
    if (!workspaceId || !projectId) return;
    try {
      setLoading(true);
      setError(null);
      const result = await ProjectService.getProject(workspaceId, projectId);
      setData(result);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : "Failed to fetch project";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [workspaceId, projectId]);

  useEffect(() => {
    if (workspaceId && projectId) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      fetchProject();
    }
  }, [fetchProject, workspaceId, projectId]);

  const updateProject = async (payload: ProjectUpdate) => {
    const result = await ProjectService.updateProject(workspaceId, projectId, payload);
    setData(result);
    return result;
  };

  const deleteProject = async () => {
    await ProjectService.deleteProject(workspaceId, projectId);
    setData(null);
  };

  return {
    data,
    loading,
    error,
    fetchProject,
    updateProject,
    deleteProject,
  };
}
