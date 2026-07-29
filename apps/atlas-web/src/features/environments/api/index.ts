import { request, withAuth } from "@/lib/api";
import {
  EnvironmentRead,
  EnvironmentList,
  EnvironmentCreate,
  EnvironmentUpdate,
} from "../types";

export const environmentsApi = {
  list(token: string, workspaceId: string, projectId: string, skip = 0, limit = 50): Promise<EnvironmentList> {
    return request<EnvironmentList>(`/workspaces/${workspaceId}/projects/${projectId}/environments/?skip=${skip}&limit=${limit}`, {
      headers: withAuth(token),
    });
  },

  get(token: string, workspaceId: string, projectId: string, environmentId: string): Promise<EnvironmentRead> {
    return request<EnvironmentRead>(`/workspaces/${workspaceId}/projects/${projectId}/environments/${environmentId}`, {
      headers: withAuth(token),
    });
  },

  create(token: string, workspaceId: string, projectId: string, payload: EnvironmentCreate): Promise<EnvironmentRead> {
    return request<EnvironmentRead>(`/workspaces/${workspaceId}/projects/${projectId}/environments/`, {
      method: "POST",
      headers: withAuth(token),
      body: JSON.stringify(payload),
    });
  },

  update(token: string, workspaceId: string, projectId: string, environmentId: string, payload: EnvironmentUpdate): Promise<EnvironmentRead> {
    return request<EnvironmentRead>(`/workspaces/${workspaceId}/projects/${projectId}/environments/${environmentId}`, {
      method: "PATCH",
      headers: withAuth(token),
      body: JSON.stringify(payload),
    });
  },

  delete(token: string, workspaceId: string, projectId: string, environmentId: string): Promise<void> {
    return request<void>(`/workspaces/${workspaceId}/projects/${projectId}/environments/${environmentId}`, {
      method: "DELETE",
      headers: withAuth(token),
    });
  },
};
