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
  async getOrganizations(type: "all" | "mine" = "all", skip = 0, limit = 50): Promise<OrganizationList> {
    if (type === "mine") {
      return orgApi.listMine(skip, limit);
    }
    return orgApi.list(skip, limit);
  },

  async getOrganization(id: string): Promise<OrganizationRead> {
    return orgApi.get(id);
  },

  async createOrganization(payload: OrganizationCreate): Promise<OrganizationRead> {
    return orgApi.create(payload);
  },

  async updateOrganization(id: string, payload: OrganizationUpdate): Promise<OrganizationRead> {
    return orgApi.update(id, payload);
  },

  async deleteOrganization(id: string): Promise<void> {
    return orgApi.delete(id);
  },

  async getMembers(orgId: string, skip = 0, limit = 50): Promise<OrganizationMemberList> {
    return orgMembersApi.list(orgId, skip, limit);
  },

  async inviteMember(orgId: string, email: string, role: MemberRole = "MEMBER"): Promise<OrganizationMember> {
    return orgMembersApi.invite(orgId, email, role);
  },
};
