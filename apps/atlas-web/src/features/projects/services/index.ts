import { projectsApi } from "../api";
import {
  ProjectList,
  ProjectRead,
  ProjectCreate,
  ProjectUpdate,
} from "../types";

export const ProjectService = {
  async getProjects(token: string, workspaceId: string, skip = 0, limit = 50): Promise<ProjectList> {
    return projectsApi.list(token, workspaceId, skip, limit);
  },

  async getProject(token: string, workspaceId: string, projectId: string): Promise<ProjectRead> {
    return projectsApi.get(token, workspaceId, projectId);
  },

  async createProject(token: string, workspaceId: string, payload: ProjectCreate): Promise<ProjectRead> {
    return projectsApi.create(token, workspaceId, payload);
  },

  async updateProject(token: string, workspaceId: string, projectId: string, payload: ProjectUpdate): Promise<ProjectRead> {
    return projectsApi.update(token, workspaceId, projectId, payload);
  },

  async deleteProject(token: string, workspaceId: string, projectId: string): Promise<void> {
    return projectsApi.delete(token, workspaceId, projectId);
  },
};
