import { request } from "@/lib/api";
import {
  ProjectRead,
  ProjectList,
  ProjectCreate,
  ProjectUpdate,
} from "../types";

export const projectsApi = {
  list(workspaceId: string, skip = 0, limit = 50): Promise<ProjectList> {
    return request<ProjectList>(`/workspaces/${workspaceId}/projects/?skip=${skip}&limit=${limit}`);
  },

  get(workspaceId: string, projectId: string): Promise<ProjectRead> {
    return request<ProjectRead>(`/workspaces/${workspaceId}/projects/${projectId}`);
  },

  create(workspaceId: string, payload: ProjectCreate): Promise<ProjectRead> {
    return request<ProjectRead>(`/workspaces/${workspaceId}/projects/`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  update(workspaceId: string, projectId: string, payload: ProjectUpdate): Promise<ProjectRead> {
    return request<ProjectRead>(`/workspaces/${workspaceId}/projects/${projectId}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    });
  },

  delete(workspaceId: string, projectId: string): Promise<void> {
    return request<void>(`/workspaces/${workspaceId}/projects/${projectId}`, {
      method: "DELETE",
    });
  },
};
