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

export interface SkillRegistryEntry {
  id: string;
  path: string;
  version?: string;
  status?: string;
  default?: boolean;
}

export interface SkillWorkflowStep {
  id: string;
  description: string;
  parallelizable: boolean;
  produces: string[];
}

export interface SkillPackage {
  id: string;
  name: string;
  display_name: string;
  version: string;
  description: string;
  owners: string[];
  prompt: string;
  workflow: SkillWorkflowStep[];
  policies: Array<{ id: string; description: string; severity: string }>;
  tools: string[];
  permissions: Record<string, boolean>;
  interfaces: {
    inputs: string[];
    outputs: string[];
    requires: string[];
    produces: string[];
  };
  contracts: Record<string, string>;
  input_schema?: Record<string, unknown> | null;
  output_schema?: Record<string, unknown> | null;
  tests: string[];
  knowledge: string[];
  handoffs: Array<Record<string, unknown>>;
  success_criteria: string[];
}

export interface SkillSummary {
  valid: boolean;
  registry_entry: SkillRegistryEntry;
  skill?: SkillPackage;
  skill_id?: string;
  error?: string;
}

export interface SkillExecutionRequest {
  prompt: string;
  workspace_id?: string;
  organization_id?: string;
  user_id?: string;
  project_id?: string;
  repository_id?: string;
  session_id?: string;
  metadata?: Record<string, unknown>;
  policy_context?: Record<string, unknown>;
  step_tools?: Record<string, string[]>;
  permissions?: Record<string, unknown>;
  memory?: Record<string, unknown>;
  model?: Record<string, unknown>;
  trace?: Record<string, unknown>;
  configuration?: Record<string, unknown>;
  environment?: Record<string, unknown>;
  correlation_id?: string;
  request_metadata?: Record<string, unknown>;
  deadline?: string;
  cancelled?: boolean;
}

export interface SkillExecutionResult {
  execution_id: string;
  skill_id: string;
  status: string;
  outputs: Record<string, unknown>;
  traces: Array<Record<string, unknown>>;
  policy_violations: string[];
  dependency_warnings: string[];
  error?: string | null;
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

  listSkills: async (): Promise<{ skills: SkillSummary[] }> => {
    return request<{ skills: SkillSummary[] }>("/ai/skills");
  },

  getSkill: async (skillId: string): Promise<{ skill: SkillPackage; registry_entry: SkillRegistryEntry }> => {
    return request<{ skill: SkillPackage; registry_entry: SkillRegistryEntry }>(`/ai/skills/${skillId}`);
  },

  getSkillSchema: async (skillId: string): Promise<Record<string, unknown>> => {
    return request<Record<string, unknown>>(`/ai/skills/${skillId}/schema`);
  },

  validateSkill: async (skillId: string, manifest?: Record<string, unknown>): Promise<{ skill_id: string; valid: boolean }> => {
    return request<{ skill_id: string; valid: boolean }>("/ai/skills/validate", {
      method: "POST",
      body: JSON.stringify({ skill_id: skillId, manifest }),
    });
  },

  executeSkill: async (skillId: string, payload: SkillExecutionRequest): Promise<SkillExecutionResult> => {
    return request<SkillExecutionResult>(`/ai/skills/${skillId}/execute`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  installSkill: async (row: SkillRegistryEntry): Promise<Record<string, unknown>> => {
    return request<Record<string, unknown>>("/ai/skills/install", {
      method: "POST",
      body: JSON.stringify(row),
    });
  },

  uninstallSkill: async (skillId: string): Promise<Record<string, unknown>> => {
    return request<Record<string, unknown>>("/ai/skills/uninstall", {
      method: "POST",
      body: JSON.stringify({ skill_id: skillId }),
    });
  },

  reloadSkills: async (): Promise<Record<string, unknown>> => {
    return request<Record<string, unknown>>("/ai/skills/reload", {
      method: "POST",
    });
  },

  // Orchestration & Approvals
  executeGraph: async (graphDef: Record<string, unknown>, baseRequest: Record<string, unknown>): Promise<{ execution_id: string; status: string }> => {
    return request<{ execution_id: string; status: string }>("/ai/orchestration/execute", {
      method: "POST",
      body: JSON.stringify({ graph: graphDef, base_request: baseRequest }),
    });
  },

  getExecutionState: async (executionId: string): Promise<Record<string, unknown>> => {
    return request<Record<string, unknown>>(`/ai/orchestration/${executionId}`);
  },

  listApprovals: async (): Promise<Record<string, unknown>> => {
    return request<Record<string, unknown>>("/ai/approvals");
  },

  resolveApproval: async (approvalId: string, status: string, resolvedBy: string, reason?: string): Promise<Record<string, unknown>> => {
    return request<Record<string, unknown>>(`/ai/approvals/${approvalId}/resolve`, {
      method: "POST",
      body: JSON.stringify({ status, resolved_by: resolvedBy, reason }),
    });
  },

  getOrgMemory: async (): Promise<Record<string, unknown>> => {
    return request<Record<string, unknown>>("/ai/memory/org");
  },
};