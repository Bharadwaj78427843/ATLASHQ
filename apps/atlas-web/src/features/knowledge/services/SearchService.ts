import { knowledgeApi } from "../api";
import { SearchResponse } from "../types";

export const SearchService = {
  async search(token: string, workspaceId: string, query: string, limit = 10, projectId?: string): Promise<SearchResponse> {
    return knowledgeApi.search(token, workspaceId, query, limit, projectId);
  },
};
