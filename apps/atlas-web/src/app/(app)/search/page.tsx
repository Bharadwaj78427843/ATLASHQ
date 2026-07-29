"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useActiveOrganization } from "@/contexts/OrganizationContext";
import { useWorkspaces } from "@/features/workspaces/hooks/useWorkspaces";

export default function SearchRedirectPage() {
  const router = useRouter();
  const { activeOrganization, isLoading: orgLoading } = useActiveOrganization();
  const { data: workspacesData, loading: wsLoading } = useWorkspaces(activeOrganization?.id || "");

  useEffect(() => {
    if (orgLoading || wsLoading) return;
    if (!activeOrganization) { router.replace("/organizations"); return; }
    const ws = workspacesData?.items?.[0];
    if (ws) {
      // Knowledge page has an integrated search tab
      router.replace(`/organizations/${activeOrganization.id}/workspaces/${ws.id}/knowledge`);
    } else {
      router.replace(`/organizations/${activeOrganization.id}`);
    }
  }, [activeOrganization, workspacesData, orgLoading, wsLoading, router]);

  return <div className="flex items-center justify-center h-full"><span className="spinner-ring" /></div>;
}
