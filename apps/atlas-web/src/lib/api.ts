/**
 * src/lib/api.ts
 *
 * ATLAS-009 — Typed API client for the Atlas backend.
 * All requests go through /api/* which Next.js rewrites to http://localhost:8000/*.
 */

import { getAccessToken } from "./auth";

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

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  // ── DIAGNOSTIC LOG 1: token retrieval ────────────────────────────────────
  const token = getAccessToken();
  console.log("[AUTH] getAccessToken() =", token ? `${token.slice(0, 20)}…` : "NULL — no token in localStorage");
  console.log("[AUTH] localStorage key =", "atlas_access_token");
  if (typeof window !== "undefined") {
    console.log("[AUTH] raw localStorage value =", window.localStorage.getItem("atlas_access_token") ? "EXISTS" : "MISSING");
  }

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  // Support FormData which overrides Content-Type automatically if we delete it
  if (options.body instanceof FormData) {
    delete headers["Content-Type"];
  }

  // ── DIAGNOSTIC LOG 2: headers before fetch ────────────────────────────────
  console.log("[API] →", options.method ?? "GET", url);
  console.log("[API] headers built =", JSON.stringify(headers));
  console.log("[API] options.headers =", options.headers);
  console.log("[API] Authorization present?", "Authorization" in headers);

  // Check if options.headers would clobber Authorization
  const optHeaders = options.headers ?? {};
  const mergedHeaders = { ...headers, ...optHeaders };
  console.log("[API] final merged headers =", JSON.stringify(mergedHeaders));

  const res = await fetch(url, {
    ...options,
    headers: mergedHeaders,
  });

  // ── DIAGNOSTIC LOG 3: response ─────────────────────────────────────────────
  console.log("[API] ←", res.status, res.url);

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

  me(): Promise<UserRead> {
    return request<UserRead>("/auth/me");
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
};
