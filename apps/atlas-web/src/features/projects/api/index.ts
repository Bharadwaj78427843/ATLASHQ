import { request, withAuth } from "@/lib/api";
import {
  ProjectRead,
  ProjectList,
  ProjectCreate,
  ProjectUpdate,
} from "../types";

export const projectsApi = {
  list(token: string, workspaceId: string, skip = 0, limit = 50): Promise<ProjectList> {
    return request<ProjectList>(`/workspaces/${workspaceId}/projects/?skip=${skip}&limit=${limit}`, {
      headers: withAuth(token),
    });
  },

  get(token: string, workspaceId: string, projectId: string): Promise<ProjectRead> {
    return request<ProjectRead>(`/workspaces/${workspaceId}/projects/${projectId}`, {
      headers: withAuth(token),
    });
  },

  create(token: string, workspaceId: string, payload: ProjectCreate): Promise<ProjectRead> {
    return request<ProjectRead>(`/workspaces/${workspaceId}/projects/`, {
      method: "POST",
      headers: withAuth(token),
      body: JSON.stringify(payload),
    });
  },

  update(token: string, workspaceId: string, projectId: string, payload: ProjectUpdate): Promise<ProjectRead> {
    return request<ProjectRead>(`/workspaces/${workspaceId}/projects/${projectId}`, {
      method: "PATCH",
      headers: withAuth(token),
      body: JSON.stringify(payload),
    });
  },

  delete(token: string, workspaceId: string, projectId: string): Promise<void> {
    return request<void>(`/workspaces/${workspaceId}/projects/${projectId}`, {
      method: "DELETE",
      headers: withAuth(token),
    });
  },
};
