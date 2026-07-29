import { request } from "@/lib/api";
import { getAccessToken } from "@/lib/auth";

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
  getHealth: async (): Promise<any> => {
    const token = getAccessToken();
    const res = await request<any>('/ai/health', {
      headers: { Authorization: `Bearer ${token}` }
    });
    return res;
  },

  getProviders: async (): Promise<{ providers: AIProvider[] }> => {
    const token = getAccessToken();
    const res = await request<{ providers: AIProvider[] }>('/ai/providers', {
      headers: { Authorization: `Bearer ${token}` }
    });
    return res;
  },

  chat: async (prompt: string, workspaceId?: string): Promise<ChatResponse> => {
    const token = getAccessToken();
    const res = await request<ChatResponse>('/ai/chat', {
      method: "POST",
      body: JSON.stringify({ prompt, workspace_id: workspaceId }),
      headers: { Authorization: `Bearer ${token}` }
    });
    return res;
  },
};
