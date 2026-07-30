import { knowledgeApi } from "../api";
import { KnowledgeSource } from "../types";

export const RepositoryService = {
  async connectRepository(
    workspaceId: string,
    provider: string,
    repository: string,
    branch: string,
    projectId?: string
  ): Promise<KnowledgeSource> {
    return knowledgeApi.connectRepository(workspaceId, provider, repository, branch, projectId);
  },
};
