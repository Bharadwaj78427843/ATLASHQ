"use client";

import React, { use } from "react";
import { PageHeader } from "@/components/ui/PageHeader";
import { PageLayout } from "@/components/layout/PageLayout";
import { EnvironmentForm } from "@/features/environments";

export default function NewEnvironmentPage({ params }: { params: Promise<{ id: string, workspaceId: string, projectId: string }> }) {
  const resolvedParams = use(params);
  const orgId = resolvedParams.id;
  const workspaceId = resolvedParams.workspaceId;
  const projectId = resolvedParams.projectId;

  return (
    <PageLayout maxWidth="2xl">
      <PageHeader 
        title="Create Environment" 
        subtitle="Set up a new environment within your project."
        backLink={{ href: `/organizations/${orgId}/workspaces/${workspaceId}/projects/${projectId}`, label: "Back to Project" }}
      />
      <EnvironmentForm orgId={orgId} workspaceId={workspaceId} projectId={projectId} />
    </PageLayout>
  );
}
