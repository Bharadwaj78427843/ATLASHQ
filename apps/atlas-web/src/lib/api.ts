/**
 * src/lib/api.ts
 *
 * ATLAS-009 — Typed API client for the Atlas backend.
 * All requests go through /api/* which Next.js rewrites to http://localhost:8000/*.
 */

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "/api";

export interface UserRead {
  id: string;
  email: string;
  username: string;
  first_name: string | null;
  last_name: string | null;
  avatar_url: string | null;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface RegisterPayload {
  email: string;
  username: string;
  password: string;
  first_name?: string;
  last_name?: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly detail: string,
  ) {
    super(detail);
    this.name = "ApiError";
  }
}

export async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const url = `${BASE_URL}${path}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {}),
    },
  });

  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      detail = body?.detail ?? detail;
    } catch {
      /* ignore parse error */
    }
    throw new ApiError(res.status, detail);
  }

  // 204 No Content
  if (res.status === 204) return undefined as unknown as T;
  return res.json() as Promise<T>;
}

export function withAuth(token: string): HeadersInit {
  return { Authorization: `Bearer ${token}` };
}

export const api = {
  register(payload: RegisterPayload): Promise<UserRead> {
    return request<UserRead>("/auth/register", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  login(payload: LoginPayload): Promise<TokenResponse> {
    return request<TokenResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  me(accessToken: string): Promise<UserRead> {
    return request<UserRead>("/auth/me", {
      headers: withAuth(accessToken),
    });
  },
};

// ── Organizations ───────────────────────────────────────────────────────────
import {
  OrganizationRead,
  OrganizationList,
  OrganizationCreate,
  OrganizationUpdate,
  OrganizationMember,
  OrganizationMemberList,
  MemberRole,
  MemberStatus,
} from "../features/organizations/types";
import { orgApi, orgMembersApi } from "../features/organizations/api";

export type {
  OrganizationRead,
  OrganizationList,
  OrganizationCreate,
  OrganizationUpdate,
  OrganizationMember,
  OrganizationMemberList,
  MemberRole,
  MemberStatus,
};
export { orgApi, orgMembersApi };


export interface KnowledgeSource {
  id: string;
  workspace_id: string;
  project_id: string | null;
  name: string;
  source_type: string;
  storage_path: string | null;
  status: string;
  size_bytes: number | null;
  uploaded_by: string;
  created_at: string;
  updated_at: string;
}

export interface IndexJob {
  id: string;
  source_id: string;
  status: string;
  progress: number;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
}

export interface SearchResultSnippet {
  source_id: string;
  source_name: string;
  document_id: string;
  filename: string;
  content: string;
  score: number;
}

export interface SearchResponse {
  query: string;
  results: SearchResultSnippet[];
}

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
