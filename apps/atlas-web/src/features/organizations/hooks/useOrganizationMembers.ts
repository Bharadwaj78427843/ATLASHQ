import { useState, useCallback } from "react";
import { orgMembersApi, OrganizationMember, OrganizationMemberList, MemberRole } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import { getAccessToken } from "@/lib/auth";

export function useOrganizationMembers(orgId: string) {
  const { user } = useAuth();
  const [data, setData] = useState<OrganizationMemberList | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchMembers = useCallback(async (skip = 0, limit = 50) => {
    const token = getAccessToken();
    if (!token || !orgId) return;
    try {
      setLoading(true);
      setError(null);
      const result = await orgMembersApi.list(token, orgId, skip, limit);
      setData(result);
    } catch (err: any) {
      setError(err.message || "Failed to fetch members");
    } finally {
      setLoading(false);
    }
  }, [orgId, user]);

  const inviteMember = async (email: string, role: MemberRole) => {
    const token = getAccessToken();
    if (!token) throw new Error("Not authenticated");
    const result = await orgMembersApi.invite(token, orgId, email, role);
    await fetchMembers(); // Refresh
    return result;
  };

  const updateRole = async (memberId: string, role: MemberRole) => {
    const token = getAccessToken();
    if (!token) throw new Error("Not authenticated");
    const result = await orgMembersApi.updateRole(token, orgId, memberId, role);
    await fetchMembers();
    return result;
  };

  const removeMember = async (memberId: string) => {
    const token = getAccessToken();
    if (!token) throw new Error("Not authenticated");
    await orgMembersApi.remove(token, orgId, memberId);
    await fetchMembers();
  };

  const transferOwnership = async (targetUserId: string) => {
    const token = getAccessToken();
    if (!token) throw new Error("Not authenticated");
    await orgMembersApi.transferOwnership(token, orgId, targetUserId);
    await fetchMembers();
  };

  return {
    data,
    loading,
    error,
    fetchMembers,
    inviteMember,
    updateRole,
    removeMember,
    transferOwnership,
  };
}
