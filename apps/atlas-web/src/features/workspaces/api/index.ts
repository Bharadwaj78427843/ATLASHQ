import { request, withAuth } from "@/lib/api";
import {
  WorkspaceRead,
  WorkspaceList,
  WorkspaceCreate,
  WorkspaceUpdate,
} from "../types";

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
