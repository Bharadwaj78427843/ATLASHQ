import { request } from "@/lib/api";
import {
  KnowledgeSource,
  IndexJob,
  SearchResponse,
} from "../types";

export const knowledgeApi = {
  upload(workspaceId: string, file: File, projectId?: string): Promise<KnowledgeSource> {
    const formData = new FormData();
    formData.append("workspace_id", workspaceId);
    if (projectId) formData.append("project_id", projectId);
    formData.append("file", file);

    return request<KnowledgeSource>("/knowledge/upload", {
      method: "POST",
      body: formData,
    });
  },

  listSources(workspaceId: string): Promise<KnowledgeSource[]> {
    return request<KnowledgeSource[]>(`/knowledge/sources?workspace_id=${workspaceId}`);
  },

  deleteSource(sourceId: string): Promise<void> {
    return request<void>(`/knowledge/sources/${sourceId}`, {
      method: "DELETE",
    });
  },

  listJobs(sourceId: string): Promise<IndexJob[]> {
    return request<IndexJob[]>(`/knowledge/jobs?source_id=${sourceId}`);
  },

  search(workspaceId: string, query: string, limit = 10, projectId?: string): Promise<SearchResponse> {
    return request<SearchResponse>(`/knowledge/search?workspace_id=${workspaceId}`, {
      method: "POST",
      body: JSON.stringify({ query, limit, project_id: projectId }),
    });
  },

  connectRepository(
    workspaceId: string,
    provider: string,
    repository: string,
    branch: string,
    projectId?: string
  ): Promise<KnowledgeSource> {
    return request<KnowledgeSource>("/knowledge/repositories/connect", {
      method: "POST",
      body: JSON.stringify({
        workspace_id: workspaceId,
        provider,
        repository,
        branch,
        project_id: projectId,
      }),
    });
  },

  syncRepository(sourceId: string): Promise<KnowledgeSource> {
    return request<KnowledgeSource>(`/knowledge/repositories/${sourceId}/sync`, {
      method: "POST",
    });
  },
};
