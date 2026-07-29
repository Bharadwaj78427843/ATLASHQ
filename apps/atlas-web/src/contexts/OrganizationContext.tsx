"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { useOrganizations } from "@/features/organizations";
import { OrganizationRead } from "@/features/organizations/types";

interface OrganizationContextValue {
  activeOrganization: OrganizationRead | null;
  setActiveOrganizationId: (id: string) => void;
  isLoading: boolean;
  error: string | null;
}

const OrganizationContext = createContext<OrganizationContextValue | null>(null);

export function OrganizationProvider({ children }: { children: React.ReactNode }) {
  const { data, isLoading, error } = useOrganizations("mine");
  const [activeOrgId, setActiveOrgId] = useState<string | null>(null);

  useEffect(() => {
    // If no active org is set, but we loaded some, pick the first one
    if (!activeOrgId && data?.items && data.items.length > 0) {
      const saved = localStorage.getItem("atlas_active_org");
      if (saved && data.items.find((org) => org.id === saved)) {
        setActiveOrgId(saved);
      } else {
        setActiveOrgId(data.items[0].id);
      }
    }
  }, [data, activeOrgId]);

  const handleSetOrg = (id: string) => {
    setActiveOrgId(id);
    localStorage.setItem("atlas_active_org", id);
  };

  const activeOrganization = data?.items.find((org) => org.id === activeOrgId) || null;

  return (
    <OrganizationContext.Provider
      value={{
        activeOrganization,
        setActiveOrganizationId: handleSetOrg,
        isLoading,
        error,
      }}
    >
      {children}
    </OrganizationContext.Provider>
  );
}

export function useActiveOrganization() {
  const ctx = useContext(OrganizationContext);
  if (!ctx) {
    throw new Error("useActiveOrganization must be used within an OrganizationProvider");
  }
  return ctx;
}
