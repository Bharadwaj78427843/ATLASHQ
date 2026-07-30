import { request } from "@/lib/api";
import {
  EnvironmentRead,
  EnvironmentList,
  EnvironmentCreate,
  EnvironmentUpdate,
} from "../types";

export const environmentsApi = {
  list(workspaceId: string, projectId: string, skip = 0, limit = 50): Promise<EnvironmentList> {
    return request<EnvironmentList>(`/workspaces/${workspaceId}/projects/${projectId}/environments/?skip=${skip}&limit=${limit}`);
  },

  get(workspaceId: string, projectId: string, environmentId: string): Promise<EnvironmentRead> {
    return request<EnvironmentRead>(`/workspaces/${workspaceId}/projects/${projectId}/environments/${environmentId}`);
  },

  create(workspaceId: string, projectId: string, payload: EnvironmentCreate): Promise<EnvironmentRead> {
    return request<EnvironmentRead>(`/workspaces/${workspaceId}/projects/${projectId}/environments/`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  update(workspaceId: string, projectId: string, environmentId: string, payload: EnvironmentUpdate): Promise<EnvironmentRead> {
    return request<EnvironmentRead>(`/workspaces/${workspaceId}/projects/${projectId}/environments/${environmentId}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    });
  },

  delete(workspaceId: string, projectId: string, environmentId: string): Promise<void> {
    return request<void>(`/workspaces/${workspaceId}/projects/${projectId}/environments/${environmentId}`, {
      method: "DELETE",
    });
  },
};
