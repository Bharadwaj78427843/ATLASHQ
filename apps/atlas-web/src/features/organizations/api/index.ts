import { request, withAuth } from "@/lib/api";
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
  list(token: string, skip = 0, limit = 50): Promise<OrganizationList> {
    return request<OrganizationList>(`/organizations/?skip=${skip}&limit=${limit}`, {
      headers: withAuth(token),
    });
  },

  listMine(token: string, skip = 0, limit = 50): Promise<OrganizationList> {
    return request<OrganizationList>(`/organizations/me?skip=${skip}&limit=${limit}`, {
      headers: withAuth(token),
    });
  },

  get(token: string, id: string): Promise<OrganizationRead> {
    return request<OrganizationRead>(`/organizations/${id}`, {
      headers: withAuth(token),
    });
  },

  create(token: string, payload: OrganizationCreate): Promise<OrganizationRead> {
    return request<OrganizationRead>("/organizations/", {
      method: "POST",
      headers: withAuth(token),
      body: JSON.stringify(payload),
    });
  },

  update(token: string, id: string, payload: OrganizationUpdate): Promise<OrganizationRead> {
    return request<OrganizationRead>(`/organizations/${id}`, {
      method: "PATCH",
      headers: withAuth(token),
      body: JSON.stringify(payload),
    });
  },

  delete(token: string, id: string): Promise<void> {
    return request<void>(`/organizations/${id}`, {
      method: "DELETE",
      headers: withAuth(token),
    });
  },
};

export const orgMembersApi = {
  list(token: string, orgId: string, skip = 0, limit = 50): Promise<OrganizationMemberList> {
    return request<OrganizationMemberList>(`/organizations/${orgId}/members/?skip=${skip}&limit=${limit}`, {
      headers: withAuth(token),
    });
  },

  invite(token: string, orgId: string, email: string, role: MemberRole = "MEMBER"): Promise<OrganizationMember> {
    return request<OrganizationMember>(`/organizations/${orgId}/members/invite`, {
      method: "POST",
      headers: withAuth(token),
      body: JSON.stringify({ email, role }),
    });
  },

  updateRole(token: string, orgId: string, memberId: string, role: MemberRole): Promise<OrganizationMember> {
    return request<OrganizationMember>(`/organizations/${orgId}/members/${memberId}`, {
      method: "PATCH",
      headers: withAuth(token),
      body: JSON.stringify({ role }),
    });
  },

  remove(token: string, orgId: string, memberId: string): Promise<void> {
    return request<void>(`/organizations/${orgId}/members/${memberId}`, {
      method: "DELETE",
      headers: withAuth(token),
    });
  },

  acceptInvite(token: string, orgId: string, memberId: string): Promise<OrganizationMember> {
    return request<OrganizationMember>(`/organizations/${orgId}/members/${memberId}/accept`, {
      method: "POST",
      headers: withAuth(token),
    });
  },

  rejectInvite(token: string, orgId: string, memberId: string): Promise<void> {
    return request<void>(`/organizations/${orgId}/members/${memberId}/reject`, {
      method: "POST",
      headers: withAuth(token),
    });
  },

  transferOwnership(token: string, orgId: string, targetUserId: string): Promise<void> {
    return request<void>(`/organizations/${orgId}/members/transfer-owner`, {
      method: "POST",
      headers: withAuth(token),
      body: JSON.stringify({ target_user_id: targetUserId }),
    });
  },
};
