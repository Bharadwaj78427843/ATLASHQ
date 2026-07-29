import { request, withAuth } from "@/lib/api";
import {
  KnowledgeSource,
  IndexJob,
  SearchResponse,
} from "../types";

export const knowledgeApi = {
  upload(token: string, workspaceId: string, file: File, projectId?: string): Promise<KnowledgeSource> {
    const formData = new FormData();
    formData.append("workspace_id", workspaceId);
    if (projectId) formData.append("project_id", projectId);
    formData.append("file", file);

    return request<KnowledgeSource>("/knowledge/upload", {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` }, // Do not set Content-Type to application/json
      body: formData,
    });
  },

  listSources(token: string, workspaceId: string): Promise<KnowledgeSource[]> {
    return request<KnowledgeSource[]>(`/knowledge/sources?workspace_id=${workspaceId}`, {
      headers: withAuth(token),
    });
  },

  deleteSource(token: string, sourceId: string): Promise<void> {
    return request<void>(`/knowledge/sources/${sourceId}`, {
      method: "DELETE",
      headers: withAuth(token),
    });
  },

  listJobs(token: string, sourceId: string): Promise<IndexJob[]> {
    return request<IndexJob[]>(`/knowledge/jobs?source_id=${sourceId}`, {
      headers: withAuth(token),
    });
  },

  search(token: string, workspaceId: string, query: string, limit = 10, projectId?: string): Promise<SearchResponse> {
    return request<SearchResponse>(`/knowledge/search?workspace_id=${workspaceId}`, {
      method: "POST",
      headers: withAuth(token),
      body: JSON.stringify({ query, limit, project_id: projectId }),
    });
  },

  connectRepository(
    token: string,
    workspaceId: string,
    provider: string,
    repository: string,
    branch: string,
    projectId?: string
  ): Promise<KnowledgeSource> {
    return request<KnowledgeSource>("/knowledge/repositories/connect", {
      method: "POST",
      headers: withAuth(token),
      body: JSON.stringify({
        workspace_id: workspaceId,
        provider,
        repository,
        branch,
        project_id: projectId,
      }),
    });
  },
};
