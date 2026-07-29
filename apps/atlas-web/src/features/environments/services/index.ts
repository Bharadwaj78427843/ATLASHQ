import { environmentsApi } from "../api";
import {
  EnvironmentList,
  EnvironmentRead,
  EnvironmentCreate,
  EnvironmentUpdate,
} from "../types";

export const EnvironmentService = {
  async getEnvironments(token: string, workspaceId: string, projectId: string, skip = 0, limit = 50): Promise<EnvironmentList> {
    return environmentsApi.list(token, workspaceId, projectId, skip, limit);
  },

  async getEnvironment(token: string, workspaceId: string, projectId: string, environmentId: string): Promise<EnvironmentRead> {
    return environmentsApi.get(token, workspaceId, projectId, environmentId);
  },

  async createEnvironment(token: string, workspaceId: string, projectId: string, payload: EnvironmentCreate): Promise<EnvironmentRead> {
    return environmentsApi.create(token, workspaceId, projectId, payload);
  },

  async updateEnvironment(token: string, workspaceId: string, projectId: string, environmentId: string, payload: EnvironmentUpdate): Promise<EnvironmentRead> {
    return environmentsApi.update(token, workspaceId, projectId, environmentId, payload);
  },

  async deleteEnvironment(token: string, workspaceId: string, projectId: string, environmentId: string): Promise<void> {
    return environmentsApi.delete(token, workspaceId, projectId, environmentId);
  },
};
