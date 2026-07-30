import { workspacesApi } from "../api";
import {
  WorkspaceList,
  WorkspaceRead,
  WorkspaceCreate,
  WorkspaceUpdate,
} from "../types";

export const WorkspaceService = {
  async getWorkspaces(orgId: string, skip = 0, limit = 50): Promise<WorkspaceList> {
    return workspacesApi.list(orgId, skip, limit);
  },

  async getWorkspace(orgId: string, workspaceId: string): Promise<WorkspaceRead> {
    return workspacesApi.get(orgId, workspaceId);
  },

  async createWorkspace(orgId: string, payload: WorkspaceCreate): Promise<WorkspaceRead> {
    return workspacesApi.create(orgId, payload);
  },

  async updateWorkspace(orgId: string, workspaceId: string, payload: WorkspaceUpdate): Promise<WorkspaceRead> {
    return workspacesApi.update(orgId, workspaceId, payload);
  },

  async deleteWorkspace(orgId: string, workspaceId: string): Promise<void> {
    return workspacesApi.delete(orgId, workspaceId);
  },
};
