"use client";

import React, { use } from "react";
import { PageHeader } from "@/components/ui/PageHeader";
import { PageLayout } from "@/components/layout/PageLayout";
import { WorkspaceForm } from "@/features/workspaces";

export default function NewWorkspacePage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const orgId = resolvedParams.id;

  return (
    <PageLayout maxWidth="2xl">
      <PageHeader 
        title="Create Workspace" 
        subtitle="Set up a new workspace within your organization."
        backLink={{ href: `/organizations/${orgId}`, label: "Back to Organization" }}
      />
      <WorkspaceForm orgId={orgId} />
    </PageLayout>
  );
}
