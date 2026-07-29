import { knowledgeApi } from "../api";
import { KnowledgeSource } from "../types";

export const RepositoryService = {
  async connectRepository(
    token: string,
    workspaceId: string,
    provider: string,
    repository: string,
    branch: string,
    projectId?: string
  ): Promise<KnowledgeSource> {
    return knowledgeApi.connectRepository(token, workspaceId, provider, repository, branch, projectId);
  },
};
