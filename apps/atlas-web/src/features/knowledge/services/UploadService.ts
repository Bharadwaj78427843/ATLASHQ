import { knowledgeApi } from "../api";
import { KnowledgeSource } from "../types";

export const UploadService = {
  async uploadFile(token: string, workspaceId: string, file: File, projectId?: string): Promise<KnowledgeSource> {
    return knowledgeApi.upload(token, workspaceId, file, projectId);
  },
};
