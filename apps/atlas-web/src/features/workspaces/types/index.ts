export interface WorkspaceRead {
  id: string;
  organization_id: string;
  name: string;
  slug: string;
  description: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface WorkspaceCreate {
  name: string;
  slug: string;
  description?: string;
}

export interface WorkspaceUpdate {
  name?: string;
  description?: string;
  is_active?: boolean;
}

export interface WorkspaceList {
  items: WorkspaceRead[];
  total: number;
  skip: number;
  limit: number;
}
