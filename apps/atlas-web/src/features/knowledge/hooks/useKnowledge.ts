"use client";

import { useState, useCallback, useEffect } from "react";
import { SourceService, SearchService, UploadService, RepositoryService } from "../services";
import { KnowledgeSource } from "../types";

export function useKnowledge(workspaceId: string, projectId?: string) {
  const [sources, setSources] = useState<KnowledgeSource[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSources = useCallback(async () => {
    if (!workspaceId) return;
    try {
      setLoading(true);
      setError(null);
      const data = await SourceService.listSources(workspaceId);
      
      if (projectId) {
        setSources(data.filter(s => s.project_id === projectId || s.project_id === null));
      } else {
        setSources(data);
      }
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : "Failed to fetch knowledge sources";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [workspaceId, projectId]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchSources();
  }, [fetchSources]);

  const uploadDocument = async (file: File) => {
    const result = await UploadService.uploadFile(workspaceId, file, projectId);
    await fetchSources();
    return result;
  };

  const connectRepository = async (provider: string, repository: string, branch: string) => {
    const result = await RepositoryService.connectRepository(workspaceId, provider, repository, branch, projectId);
    await fetchSources();
    return result;
  };

  const syncRepository = async (sourceId: string) => {
    const result = await RepositoryService.syncRepository(sourceId);
    await fetchSources();
    return result;
  };

  const deleteSource = async (sourceId: string) => {
    await SourceService.deleteSource(sourceId);
    await fetchSources();
  };

  const search = async (query: string, limit = 10) => {
    const response = await SearchService.search(workspaceId, query, limit, projectId);
    return response.results;
  };

  return {
    sources,
    loading,
    error,
    fetchSources,
    uploadDocument,
    connectRepository,
    syncRepository,
    deleteSource,
    search,
  };
}
