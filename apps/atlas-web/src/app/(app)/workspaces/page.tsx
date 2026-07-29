"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useActiveOrganization } from "@/contexts/OrganizationContext";

export default function WorkspacesRedirectPage() {
  const router = useRouter();
  const { activeOrganization, isLoading } = useActiveOrganization();

  useEffect(() => {
    if (isLoading) return;
    if (activeOrganization) {
      router.replace(`/organizations/${activeOrganization.id}`);
    } else {
      router.replace("/organizations");
    }
  }, [activeOrganization, isLoading, router]);

  return <div className="flex items-center justify-center h-full"><span className="spinner-ring" /></div>;
}
