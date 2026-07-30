import { knowledgeApi } from "../api";
import { KnowledgeSource, IndexJob } from "../types";

export const SourceService = {
  async listSources(workspaceId: string): Promise<KnowledgeSource[]> {
    return knowledgeApi.listSources(workspaceId);
  },

  async deleteSource(sourceId: string): Promise<void> {
    return knowledgeApi.deleteSource(sourceId);
  },

  async listJobs(sourceId: string): Promise<IndexJob[]> {
    return knowledgeApi.listJobs(sourceId);
  },
};
