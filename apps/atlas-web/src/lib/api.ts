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

async function request<T>(
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

function withAuth(token: string): HeadersInit {
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

export interface OrganizationRead {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  logo_url: string | null;
  website: string | null;
  owner_id: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface OrganizationList {
  items: OrganizationRead[];
  total: number;
  skip: number;
  limit: number;
}

export interface OrganizationCreate {
  name: string;
  slug: string;
  description?: string;
  logo_url?: string;
  website?: string;
}

export interface OrganizationUpdate {
  name?: string;
  description?: string;
  logo_url?: string;
  website?: string;
}

export type MemberRole = "OWNER" | "ADMIN" | "MEMBER" | "VIEWER";
export type MemberStatus = "INVITED" | "ACTIVE" | "SUSPENDED" | "LEFT";

export interface OrganizationMember {
  id: string;
  organization_id: string;
  user_id: string;
  role: MemberRole;
  status: MemberStatus;
  invited_by_id: string | null;
  joined_at: string | null;
  created_at: string;
  updated_at: string;
  user: UserRead;
}

export interface OrganizationMemberList {
  items: OrganizationMember[];
  total: number;
  skip: number;
  limit: number;
}

export const orgApi = {
  list(token: string, skip = 0, limit = 50): Promise<OrganizationList> {
    return request<OrganizationList>(`/organizations/?skip=${skip}&limit=${limit}`, {
      headers: withAuth(token),
    });
  },

  listMine(token: string, skip = 0, limit = 50): Promise<OrganizationList> {
    return request<OrganizationList>(`/organizations/me?skip=${skip}&limit=${limit}`, {
      headers: withAuth(token),
    });
  },

  get(token: string, id: string): Promise<OrganizationRead> {
    return request<OrganizationRead>(`/organizations/${id}`, {
      headers: withAuth(token),
    });
  },

  create(token: string, payload: OrganizationCreate): Promise<OrganizationRead> {
    return request<OrganizationRead>("/organizations/", {
      method: "POST",
      headers: withAuth(token),
      body: JSON.stringify(payload),
    });
  },

  update(token: string, id: string, payload: OrganizationUpdate): Promise<OrganizationRead> {
    return request<OrganizationRead>(`/organizations/${id}`, {
      method: "PATCH",
      headers: withAuth(token),
      body: JSON.stringify(payload),
    });
  },

  delete(token: string, id: string): Promise<void> {
    return request<void>(`/organizations/${id}`, {
      method: "DELETE",
      headers: withAuth(token),
    });
  },
};

export const orgMembersApi = {
  list(token: string, orgId: string, skip = 0, limit = 50): Promise<OrganizationMemberList> {
    return request<OrganizationMemberList>(`/organizations/${orgId}/members/?skip=${skip}&limit=${limit}`, {
      headers: withAuth(token),
    });
  },

  invite(token: string, orgId: string, email: string, role: MemberRole = "MEMBER"): Promise<OrganizationMember> {
    return request<OrganizationMember>(`/organizations/${orgId}/members/invite`, {
      method: "POST",
      headers: withAuth(token),
      body: JSON.stringify({ email, role }),
    });
  },

  updateRole(token: string, orgId: string, memberId: string, role: MemberRole): Promise<OrganizationMember> {
    return request<OrganizationMember>(`/organizations/${orgId}/members/${memberId}`, {
      method: "PATCH",
      headers: withAuth(token),
      body: JSON.stringify({ role }),
    });
  },

  remove(token: string, orgId: string, memberId: string): Promise<void> {
    return request<void>(`/organizations/${orgId}/members/${memberId}`, {
      method: "DELETE",
      headers: withAuth(token),
    });
  },

  acceptInvite(token: string, orgId: string, memberId: string): Promise<OrganizationMember> {
    return request<OrganizationMember>(`/organizations/${orgId}/members/${memberId}/accept`, {
      method: "POST",
      headers: withAuth(token),
    });
  },

  rejectInvite(token: string, orgId: string, memberId: string): Promise<void> {
    return request<void>(`/organizations/${orgId}/members/${memberId}/reject`, {
      method: "POST",
      headers: withAuth(token),
    });
  },

  transferOwnership(token: string, orgId: string, targetUserId: string): Promise<void> {
    return request<void>(`/organizations/${orgId}/members/transfer-owner`, {
      method: "POST",
      headers: withAuth(token),
      body: JSON.stringify({ target_user_id: targetUserId }),
    });
  },
};

// ── Workspaces ──────────────────────────────────────────────────────────────

export interface WorkspaceRead {
  id: string;
  organization_id: string;
  name: string;
  slug: string;
  description: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface WorkspaceCreate {
  name: string;
  slug: string;
  description?: string;
}

export interface WorkspaceUpdate {
  name?: string;
  description?: string;
  is_active?: boolean;
}

export interface WorkspaceList {
  items: WorkspaceRead[];
  total: number;
  skip: number;
  limit: number;
}

export const workspacesApi = {
  list(token: string, orgId: string, skip = 0, limit = 50): Promise<WorkspaceList> {
    return request<WorkspaceList>(`/organizations/${orgId}/workspaces/?skip=${skip}&limit=${limit}`, {
      headers: withAuth(token),
    });
  },

  get(token: string, orgId: string, workspaceId: string): Promise<WorkspaceRead> {
    return request<WorkspaceRead>(`/organizations/${orgId}/workspaces/${workspaceId}`, {
      headers: withAuth(token),
    });
  },

  create(token: string, orgId: string, payload: WorkspaceCreate): Promise<WorkspaceRead> {
    return request<WorkspaceRead>(`/organizations/${orgId}/workspaces/`, {
      method: "POST",
      headers: withAuth(token),
      body: JSON.stringify(payload),
    });
  },

  update(token: string, orgId: string, workspaceId: string, payload: WorkspaceUpdate): Promise<WorkspaceRead> {
    return request<WorkspaceRead>(`/organizations/${orgId}/workspaces/${workspaceId}`, {
      method: "PATCH",
      headers: withAuth(token),
      body: JSON.stringify(payload),
    });
  },

  delete(token: string, orgId: string, workspaceId: string): Promise<void> {
    return request<void>(`/organizations/${orgId}/workspaces/${workspaceId}`, {
      method: "DELETE",
      headers: withAuth(token),
    });
  },
};
