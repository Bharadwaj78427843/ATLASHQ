import { request } from "@/lib/api";
import { 
  OrganizationList, 
  OrganizationRead, 
  OrganizationCreate, 
  OrganizationUpdate,
  OrganizationMemberList,
  OrganizationMember,
  MemberRole
} from "../types";

export const orgApi = {
  list(skip = 0, limit = 50): Promise<OrganizationList> {
    return request<OrganizationList>(`/organizations/?skip=${skip}&limit=${limit}`);
  },

  listMine(skip = 0, limit = 50): Promise<OrganizationList> {
    return request<OrganizationList>(`/organizations/me?skip=${skip}&limit=${limit}`);
  },

  get(id: string): Promise<OrganizationRead> {
    return request<OrganizationRead>(`/organizations/${id}`);
  },

  create(payload: OrganizationCreate): Promise<OrganizationRead> {
    return request<OrganizationRead>("/organizations/", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  update(id: string, payload: OrganizationUpdate): Promise<OrganizationRead> {
    return request<OrganizationRead>(`/organizations/${id}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    });
  },

  delete(id: string): Promise<void> {
    return request<void>(`/organizations/${id}`, {
      method: "DELETE",
    });
  },
};

export const orgMembersApi = {
  list(orgId: string, skip = 0, limit = 50): Promise<OrganizationMemberList> {
    return request<OrganizationMemberList>(`/organizations/${orgId}/members/?skip=${skip}&limit=${limit}`);
  },

  invite(orgId: string, email: string, role: MemberRole = "MEMBER"): Promise<OrganizationMember> {
    return request<OrganizationMember>(`/organizations/${orgId}/members/invite`, {
      method: "POST",
      body: JSON.stringify({ email, role }),
    });
  },

  updateRole(orgId: string, memberId: string, role: MemberRole): Promise<OrganizationMember> {
    return request<OrganizationMember>(`/organizations/${orgId}/members/${memberId}`, {
      method: "PATCH",
      body: JSON.stringify({ role }),
    });
  },

  remove(orgId: string, memberId: string): Promise<void> {
    return request<void>(`/organizations/${orgId}/members/${memberId}`, {
      method: "DELETE",
    });
  },

  acceptInvite(orgId: string, memberId: string): Promise<OrganizationMember> {
    return request<OrganizationMember>(`/organizations/${orgId}/members/${memberId}/accept`, {
      method: "POST",
    });
  },

  rejectInvite(orgId: string, memberId: string): Promise<void> {
    return request<void>(`/organizations/${orgId}/members/${memberId}/reject`, {
      method: "POST",
    });
  },

  transferOwnership(orgId: string, targetUserId: string): Promise<void> {
    return request<void>(`/organizations/${orgId}/members/transfer-owner`, {
      method: "POST",
      body: JSON.stringify({ target_user_id: targetUserId }),
    });
  },
};
