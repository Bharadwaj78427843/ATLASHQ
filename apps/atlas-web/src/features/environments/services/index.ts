import { environmentsApi } from "../api";
import {
  EnvironmentList,
  EnvironmentRead,
  EnvironmentCreate,
  EnvironmentUpdate,
} from "../types";

export const EnvironmentService = {
  async getEnvironments(workspaceId: string, projectId: string, skip = 0, limit = 50): Promise<EnvironmentList> {
    return environmentsApi.list(workspaceId, projectId, skip, limit);
  },

  async getEnvironment(workspaceId: string, projectId: string, environmentId: string): Promise<EnvironmentRead> {
    return environmentsApi.get(workspaceId, projectId, environmentId);
  },

  async createEnvironment(workspaceId: string, projectId: string, payload: EnvironmentCreate): Promise<EnvironmentRead> {
    return environmentsApi.create(workspaceId, projectId, payload);
  },

  async updateEnvironment(workspaceId: string, projectId: string, environmentId: string, payload: EnvironmentUpdate): Promise<EnvironmentRead> {
    return environmentsApi.update(workspaceId, projectId, environmentId, payload);
  },

  async deleteEnvironment(workspaceId: string, projectId: string, environmentId: string): Promise<void> {
    return environmentsApi.delete(workspaceId, projectId, environmentId);
  },
};
