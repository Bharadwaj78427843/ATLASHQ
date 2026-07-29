export type EnvironmentType = "DEVELOPMENT" | "PREVIEW" | "STAGING" | "PRODUCTION";

export interface EnvironmentRead {
  id: string;
  project_id: string;
  name: string;
  type: EnvironmentType;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface EnvironmentCreate {
  name: string;
  type: EnvironmentType;
}

export interface EnvironmentUpdate {
  name?: string;
  type?: EnvironmentType;
  is_active?: boolean;
}

export interface EnvironmentList {
  items: EnvironmentRead[];
  total: number;
  skip: number;
  limit: number;
}
