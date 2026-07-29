import { knowledgeApi } from "../api";
import { KnowledgeSource, IndexJob } from "../types";

export const SourceService = {
  async listSources(token: string, workspaceId: string): Promise<KnowledgeSource[]> {
    return knowledgeApi.listSources(token, workspaceId);
  },

  async deleteSource(token: string, sourceId: string): Promise<void> {
    return knowledgeApi.deleteSource(token, sourceId);
  },

  async listJobs(token: string, sourceId: string): Promise<IndexJob[]> {
    return knowledgeApi.listJobs(token, sourceId);
  },
};
