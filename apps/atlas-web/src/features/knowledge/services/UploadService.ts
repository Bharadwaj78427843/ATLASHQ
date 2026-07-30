import { knowledgeApi } from "../api";
import { KnowledgeSource } from "../types";

export const UploadService = {
  async uploadFile(workspaceId: string, file: File, projectId?: string): Promise<KnowledgeSource> {
    return knowledgeApi.upload(workspaceId, file, projectId);
  },
};
