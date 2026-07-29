"use client";

import { useState, useCallback, useEffect } from "react";
import { SourceService, SearchService, UploadService, RepositoryService } from "../services";
import { KnowledgeSource, SearchResultSnippet } from "../types";
import { getAccessToken } from "@/lib/auth";

export function useKnowledge(workspaceId: string, projectId?: string) {
  const [sources, setSources] = useState<KnowledgeSource[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSources = useCallback(async () => {
    const token = getAccessToken();
    if (!token || !workspaceId) return;
    try {
      setLoading(true);
      setError(null);
      const data = await SourceService.listSources(token, workspaceId);
      
      if (projectId) {
        setSources(data.filter(s => s.project_id === projectId || s.project_id === null));
      } else {
        setSources(data);
      }
    } catch (err: any) {
      setError(err.message || "Failed to fetch knowledge sources");
    } finally {
      setLoading(false);
    }
  }, [workspaceId, projectId]);

  useEffect(() => {
    fetchSources();
  }, [fetchSources]);

  const uploadDocument = async (file: File) => {
    const token = getAccessToken();
    if (!token) throw new Error("Not authenticated");
    const result = await UploadService.uploadFile(token, workspaceId, file, projectId);
    await fetchSources();
    return result;
  };

  const connectRepository = async (provider: string, repository: string, branch: string) => {
    const token = getAccessToken();
    if (!token) throw new Error("Not authenticated");
    const result = await RepositoryService.connectRepository(token, workspaceId, provider, repository, branch, projectId);
    await fetchSources();
    return result;
  };

  const deleteSource = async (sourceId: string) => {
    const token = getAccessToken();
    if (!token) throw new Error("Not authenticated");
    await SourceService.deleteSource(token, sourceId);
    await fetchSources();
  };

  const search = async (query: string, limit = 10) => {
    const token = getAccessToken();
    if (!token) throw new Error("Not authenticated");
    const response = await SearchService.search(token, workspaceId, query, limit, projectId);
    return response.results;
  };

  return {
    sources,
    loading,
    error,
    fetchSources,
    uploadDocument,
    connectRepository,
    deleteSource,
    search,
  };
}
