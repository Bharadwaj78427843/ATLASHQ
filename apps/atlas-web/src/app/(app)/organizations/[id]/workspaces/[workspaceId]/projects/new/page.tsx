"use client";

import React, { use } from "react";
import { PageHeader } from "@/components/ui/PageHeader";
import { PageLayout } from "@/components/layout/PageLayout";
import { ProjectForm } from "@/features/projects";

export default function NewProjectPage({ params }: { params: Promise<{ id: string, workspaceId: string }> }) {
  const resolvedParams = use(params);
  const orgId = resolvedParams.id;
  const workspaceId = resolvedParams.workspaceId;

  return (
    <PageLayout maxWidth="2xl">
      <PageHeader 
        title="Create Project" 
        subtitle="Set up a new project within your workspace."
        backLink={{ href: `/organizations/${orgId}/workspaces/${workspaceId}`, label: "Back to Workspace" }}
      />
      <ProjectForm orgId={orgId} workspaceId={workspaceId} />
    </PageLayout>
  );
}
