"use client";

import { useEffect, useMemo, useState } from "react";
import { useActiveOrganization } from "@/contexts/OrganizationContext";
import { useWorkspaces } from "@/features/workspaces/hooks/useWorkspaces";
import type { WorkspaceRead } from "@/features/workspaces/types";

function workspaceStorageKey(orgId: string): string {
  return `atlas_active_workspace_${orgId}`;
}

export function useWorkspaceSelection() {
  const { activeOrganization, isLoading: orgLoading } = useActiveOrganization();
  const orgId = activeOrganization?.id ?? "";
  const { data: workspacesData, loading: workspaceLoading } = useWorkspaces(orgId);
  const [activeWorkspaceId, setActiveWorkspaceId] = useState<string>("");

  const workspaces = workspacesData?.items ?? [];

  useEffect(() => {
    if (!orgId || workspaces.length === 0) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setActiveWorkspaceId("");
      return;
    }

    const key = workspaceStorageKey(orgId);
    const saved = localStorage.getItem(key);

    if (saved && workspaces.some((ws) => ws.id === saved)) {
      setActiveWorkspaceId(saved);
      return;
    }

    setActiveWorkspaceId(workspaces[0].id);
  }, [orgId, workspaces]);

  const activeWorkspace = useMemo<WorkspaceRead | null>(() => {
    if (workspaces.length === 0) {
      return null;
    }

    return workspaces.find((ws) => ws.id === activeWorkspaceId) ?? workspaces[0];
  }, [workspaces, activeWorkspaceId]);

  const setWorkspaceId = (workspaceId: string) => {
    if (!orgId) {
      return;
    }

    setActiveWorkspaceId(workspaceId);
    localStorage.setItem(workspaceStorageKey(orgId), workspaceId);
  };

  return {
    activeOrganization,
    workspaces,
    activeWorkspace,
    setWorkspaceId,
    isLoading: orgLoading || workspaceLoading,
  };
}
