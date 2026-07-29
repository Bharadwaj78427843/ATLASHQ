import { UserRead } from "@/lib/api";

export interface OrganizationRead {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  logo_url: string | null;
  website: string | null;
  owner_id: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface OrganizationList {
  items: OrganizationRead[];
  total: number;
  skip: number;
  limit: number;
}

export interface OrganizationCreate {
  name: string;
  slug: string;
  description?: string;
  logo_url?: string;
  website?: string;
}

export interface OrganizationUpdate {
  name?: string;
  description?: string;
  logo_url?: string;
  website?: string;
}

export type MemberRole = "OWNER" | "ADMIN" | "MEMBER" | "VIEWER";
export type MemberStatus = "INVITED" | "ACTIVE" | "SUSPENDED" | "LEFT";

export interface OrganizationMember {
  id: string;
  organization_id: string;
  user_id: string;
  role: MemberRole;
  status: MemberStatus;
  invited_by_id: string | null;
  joined_at: string | null;
  created_at: string;
  updated_at: string;
  user: UserRead;
}

export interface OrganizationMemberList {
  items: OrganizationMember[];
  total: number;
  skip: number;
  limit: number;
}
