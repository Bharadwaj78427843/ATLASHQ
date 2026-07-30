import { request } from "@/lib/api";

export interface AIProvider {
  category: string;
  name: string;
  is_active: boolean;
  health_status: string;
  health_message: string;
}

export interface ChatResponse {
  response: string;
  context_used: boolean;
  model: string;
  chunks: string[];
}

export const aiApi = {
  getHealth: async (): Promise<Record<string, unknown>> => {
    return request<Record<string, unknown>>('/ai/health');
  },

  getProviders: async (): Promise<{ providers: AIProvider[] }> => {
    return request<{ providers: AIProvider[] }>('/ai/providers');
  },

  chat: async (prompt: string, workspaceId?: string): Promise<ChatResponse> => {
    return request<ChatResponse>('/ai/chat', {
      method: "POST",
      body: JSON.stringify({ prompt, workspace_id: workspaceId }),
    });
  },
};
