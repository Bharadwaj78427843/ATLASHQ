"use client";

import { useState, useCallback } from "react";
import { orgMembersApi } from "../api";
import { OrganizationMemberList, MemberRole } from "../types";


export function useOrganizationMembers(orgId: string) {
  const [data, setData] = useState<OrganizationMemberList | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchMembers = useCallback(async (skip = 0, limit = 50) => {
    if (!orgId) return;
    try {
      setLoading(true);
      setError(null);
      const result = await orgMembersApi.list(orgId, skip, limit);
      setData(result);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : "Failed to fetch members";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [orgId]);

  const inviteMember = async (email: string, role: MemberRole) => {
    const result = await orgMembersApi.invite(orgId, email, role);
    await fetchMembers(); // Refresh
    return result;
  };

  const updateRole = async (memberId: string, role: MemberRole) => {
    const result = await orgMembersApi.updateRole(orgId, memberId, role);
    await fetchMembers();
    return result;
  };

  const removeMember = async (memberId: string) => {
    await orgMembersApi.remove(orgId, memberId);
    await fetchMembers();
  };

  const transferOwnership = async (targetUserId: string) => {
    await orgMembersApi.transferOwnership(orgId, targetUserId);
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
