"use client";

import React, { useEffect, useState, use } from "react";
import Link from "next/link";
import { useOrganizationMembers } from "@/hooks/useOrganizationMembers";
import { useOrganization } from "@/hooks/useOrganizations";
import { MemberRole } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";

export default function OrganizationMembersPage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const orgId = resolvedParams.id;

  const { user } = useAuth();
  const { data: orgData } = useOrganization(orgId);
  const { 
    data: membersData, loading, error, 
    fetchMembers, inviteMember, updateRole, removeMember, transferOwnership 
  } = useOrganizationMembers(orgId);

  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState<MemberRole>("MEMBER");
  const [isInviting, setIsInviting] = useState(false);
  const [inviteError, setInviteError] = useState<string | null>(null);

  useEffect(() => {
    fetchMembers();
  }, [fetchMembers]);

  const isOwner = user?.id === orgData?.owner_id;
  const currentMember = membersData?.items.find(m => m.user_id === user?.id);
  const canManage = currentMember?.role === "OWNER" || currentMember?.role === "ADMIN";

  async function handleInvite(e: React.FormEvent) {
    e.preventDefault();
    if (!inviteEmail) return;
    setIsInviting(true);
    setInviteError(null);
    try {
      await inviteMember(inviteEmail, inviteRole);
      setInviteEmail("");
      setInviteRole("MEMBER");
    } catch (err: any) {
      setInviteError(err.message || "Failed to invite user");
    } finally {
      setIsInviting(false);
    }
  }

  async function handleUpdateRole(memberId: string, newRole: MemberRole) {
    try {
      await updateRole(memberId, newRole);
    } catch (err: any) {
      alert(err.message || "Failed to update role");
    }
  }

  async function handleRemove(memberId: string) {
    if (!confirm("Are you sure you want to remove this member?")) return;
    try {
      await removeMember(memberId);
    } catch (err: any) {
      alert(err.message || "Failed to remove member");
    }
  }

  async function handleTransferOwnership(targetUserId: string) {
    if (!confirm("Are you sure you want to transfer ownership to this user? You will become an ADMIN.")) return;
    try {
      await transferOwnership(targetUserId);
    } catch (err: any) {
      alert(err.message || "Failed to transfer ownership");
    }
  }

  if (loading && !membersData) {
    return <div style={{ display: "flex", justifyContent: "center", padding: "60px 0" }}><span className="spinner-ring" /></div>;
  }

  return (
    <div style={{ maxWidth: "800px", margin: "0 auto", paddingBottom: "40px" }}>
      <div style={{ marginBottom: "32px" }}>
        <Link href={`/organizations/${orgId}`} style={{ color: "var(--text-secondary)", textDecoration: "none", fontSize: "14px", display: "inline-block", marginBottom: "16px" }}>
          ← Back to Organization
        </Link>
        <h1 className="hero-title" style={{ fontSize: "28px", margin: 0 }}>Manage Members</h1>
        <p style={{ color: "var(--text-secondary)", marginTop: "8px" }}>
          {orgData?.name}
        </p>
      </div>

      {error && (
        <div className="alert alert-error" style={{ marginBottom: "24px" }}>
          {error}
        </div>
      )}

      {canManage && (
        <div className="profile-card" style={{ marginBottom: "32px" }}>
          <h2 className="profile-card-title">Invite New Member</h2>
          {inviteError && <div className="alert alert-error" style={{ marginBottom: "16px" }}>{inviteError}</div>}
          <form onSubmit={handleInvite} style={{ display: "flex", gap: "12px", alignItems: "flex-end", flexWrap: "wrap" }}>
            <div className="form-group" style={{ marginBottom: 0, flex: "1 1 200px" }}>
              <label className="form-label" htmlFor="invite-email">Email</label>
              <input
                id="invite-email"
                type="email"
                required
                className="form-input"
                placeholder="user@example.com"
                value={inviteEmail}
                onChange={(e) => setInviteEmail(e.target.value)}
              />
            </div>
            <div className="form-group" style={{ marginBottom: 0, width: "150px" }}>
              <label className="form-label" htmlFor="invite-role">Role</label>
              <select 
                id="invite-role" 
                className="form-input" 
                value={inviteRole} 
                onChange={(e) => setInviteRole(e.target.value as MemberRole)}
              >
                <option value="VIEWER">Viewer</option>
                <option value="MEMBER">Member</option>
                <option value="ADMIN">Admin</option>
              </select>
            </div>
            <button type="submit" className="btn-primary" disabled={isInviting}>
              {isInviting ? "Inviting..." : "Send Invite"}
            </button>
          </form>
        </div>
      )}

      <div className="profile-card" style={{ padding: 0, overflow: "hidden" }}>
        <div style={{ padding: "20px 24px", borderBottom: "1px solid var(--border)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h2 className="profile-card-title" style={{ margin: 0, padding: 0, border: "none" }}>Team Members</h2>
          <span style={{ color: "var(--text-secondary)", fontSize: "14px" }}>{membersData?.total || 0} total</span>
        </div>

        <div style={{ display: "flex", flexDirection: "column" }}>
          {membersData?.items.map((member) => (
            <div key={member.id} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "16px 24px", borderBottom: "1px solid var(--border)" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                <div className="avatar" style={{ width: "40px", height: "40px", fontSize: "16px" }}>
                  {member.user.first_name?.[0]?.toUpperCase() || member.user.username[0].toUpperCase()}
                </div>
                <div>
                  <div style={{ fontWeight: 500 }}>{member.user.first_name} {member.user.last_name}</div>
                  <div style={{ color: "var(--text-secondary)", fontSize: "14px" }}>{member.user.email}</div>
                  {member.status === "INVITED" && <span className="badge badge-blue" style={{ marginTop: "4px" }}>Pending Invite</span>}
                </div>
              </div>
              
              <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
                {canManage && member.role !== "OWNER" && member.user_id !== user?.id ? (
                  <select 
                    className="form-input" 
                    style={{ width: "110px", padding: "6px 12px", height: "auto" }}
                    value={member.role}
                    onChange={(e) => handleUpdateRole(member.id, e.target.value as MemberRole)}
                  >
                    <option value="VIEWER">Viewer</option>
                    <option value="MEMBER">Member</option>
                    <option value="ADMIN">Admin</option>
                  </select>
                ) : (
                  <span className="code-pill">{member.role}</span>
                )}

                {isOwner && member.role === "ADMIN" && member.status === "ACTIVE" && (
                   <button className="btn-ghost" style={{ fontSize: "12px", padding: "4px 8px" }} onClick={() => handleTransferOwnership(member.user_id)}>
                     Make Owner
                   </button>
                )}

                {(canManage || member.user_id === user?.id) && member.role !== "OWNER" && (
                  <button className="btn-ghost" style={{ color: "var(--error)", padding: "6px 12px" }} onClick={() => handleRemove(member.id)}>
                    {member.user_id === user?.id ? "Leave" : "Remove"}
                  </button>
                )}
              </div>
            </div>
          ))}
          {membersData?.items.length === 0 && (
            <div style={{ padding: "32px", textAlign: "center", color: "var(--text-secondary)" }}>
              No members found.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
