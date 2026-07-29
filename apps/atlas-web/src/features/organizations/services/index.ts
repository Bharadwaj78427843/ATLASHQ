import { orgApi, orgMembersApi } from "../api";
import { 
  OrganizationList, 
  OrganizationRead, 
  OrganizationCreate, 
  OrganizationUpdate,
  OrganizationMemberList,
  OrganizationMember,
  MemberRole
} from "../types";

export const OrganizationService = {
  async getOrganizations(token: string, type: "all" | "mine" = "all", skip = 0, limit = 50): Promise<OrganizationList> {
    if (type === "mine") {
      return orgApi.listMine(token, skip, limit);
    }
    return orgApi.list(token, skip, limit);
  },

  async getOrganization(token: string, id: string): Promise<OrganizationRead> {
    return orgApi.get(token, id);
  },

  async createOrganization(token: string, payload: OrganizationCreate): Promise<OrganizationRead> {
    return orgApi.create(token, payload);
  },

  async updateOrganization(token: string, id: string, payload: OrganizationUpdate): Promise<OrganizationRead> {
    return orgApi.update(token, id, payload);
  },

  async deleteOrganization(token: string, id: string): Promise<void> {
    return orgApi.delete(token, id);
  },

  async getMembers(token: string, orgId: string, skip = 0, limit = 50): Promise<OrganizationMemberList> {
    return orgMembersApi.list(token, orgId, skip, limit);
  },

  async inviteMember(token: string, orgId: string, email: string, role: MemberRole = "MEMBER"): Promise<OrganizationMember> {
    return orgMembersApi.invite(token, orgId, email, role);
  },
};
