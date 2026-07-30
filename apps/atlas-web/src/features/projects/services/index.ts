import { projectsApi } from "../api";
import {
  ProjectList,
  ProjectRead,
  ProjectCreate,
  ProjectUpdate,
} from "../types";

export const ProjectService = {
  async getProjects(workspaceId: string, skip = 0, limit = 50): Promise<ProjectList> {
    return projectsApi.list(workspaceId, skip, limit);
  },

  async getProject(workspaceId: string, projectId: string): Promise<ProjectRead> {
    return projectsApi.get(workspaceId, projectId);
  },

  async createProject(workspaceId: string, payload: ProjectCreate): Promise<ProjectRead> {
    return projectsApi.create(workspaceId, payload);
  },

  async updateProject(workspaceId: string, projectId: string, payload: ProjectUpdate): Promise<ProjectRead> {
    return projectsApi.update(workspaceId, projectId, payload);
  },

  async deleteProject(workspaceId: string, projectId: string): Promise<void> {
    return projectsApi.delete(workspaceId, projectId);
  },
};
