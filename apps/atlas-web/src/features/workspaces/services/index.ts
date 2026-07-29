import { workspacesApi } from "../api";
import {
  WorkspaceList,
  WorkspaceRead,
  WorkspaceCreate,
  WorkspaceUpdate,
} from "../types";

export const WorkspaceService = {
  async getWorkspaces(token: string, orgId: string, skip = 0, limit = 50): Promise<WorkspaceList> {
    return workspacesApi.list(token, orgId, skip, limit);
  },

  async getWorkspace(token: string, orgId: string, workspaceId: string): Promise<WorkspaceRead> {
    return workspacesApi.get(token, orgId, workspaceId);
  },

  async createWorkspace(token: string, orgId: string, payload: WorkspaceCreate): Promise<WorkspaceRead> {
    return workspacesApi.create(token, orgId, payload);
  },

  async updateWorkspace(token: string, orgId: string, workspaceId: string, payload: WorkspaceUpdate): Promise<WorkspaceRead> {
    return workspacesApi.update(token, orgId, workspaceId, payload);
  },

  async deleteWorkspace(token: string, orgId: string, workspaceId: string): Promise<void> {
    return workspacesApi.delete(token, orgId, workspaceId);
  },
};
