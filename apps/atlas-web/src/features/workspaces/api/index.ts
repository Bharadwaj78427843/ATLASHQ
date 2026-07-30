import { request } from "@/lib/api";
import {
  WorkspaceRead,
  WorkspaceList,
  WorkspaceCreate,
  WorkspaceUpdate,
} from "../types";

export const workspacesApi = {
  list(orgId: string, skip = 0, limit = 50): Promise<WorkspaceList> {
    return request<WorkspaceList>(`/organizations/${orgId}/workspaces/?skip=${skip}&limit=${limit}`);
  },

  get(orgId: string, workspaceId: string): Promise<WorkspaceRead> {
    return request<WorkspaceRead>(`/organizations/${orgId}/workspaces/${workspaceId}`);
  },

  create(orgId: string, payload: WorkspaceCreate): Promise<WorkspaceRead> {
    return request<WorkspaceRead>(`/organizations/${orgId}/workspaces/`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  update(orgId: string, workspaceId: string, payload: WorkspaceUpdate): Promise<WorkspaceRead> {
    return request<WorkspaceRead>(`/organizations/${orgId}/workspaces/${workspaceId}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    });
  },

  delete(orgId: string, workspaceId: string): Promise<void> {
    return request<void>(`/organizations/${orgId}/workspaces/${workspaceId}`, {
      method: "DELETE",
    });
  },
};
