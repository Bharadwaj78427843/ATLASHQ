"use client";

import React, { use } from "react";
import Link from "next/link";
import { PageHeader } from "@/components/ui/PageHeader";
import { PageLayout } from "@/components/layout/PageLayout";
import { ProjectsList } from "@/features/projects/components/ProjectsList";
import { Button } from "@/components/ui/Button";
import { Plus } from "lucide-react";

export default function WorkspaceProjectsPage({ params }: { params: Promise<{ id: string; workspaceId: string }> }) {
  const resolvedParams = use(params);
  const { id: orgId, workspaceId } = resolvedParams;

  return (
    <PageLayout>
      <PageHeader
        title="Projects"
        subtitle="Manage and organize all projects within this workspace."
        backLink={{ href: `/organizations/${orgId}/workspaces/${workspaceId}`, label: "Back to Workspace" }}
      >
        <Link href={`/organizations/${orgId}/workspaces/${workspaceId}/projects/new`}>
          <Button variant="primary">
            <Plus className="w-4 h-4 mr-2" />
            New Project
          </Button>
        </Link>
      </PageHeader>

      <ProjectsList orgId={orgId} workspaceId={workspaceId} />
    </PageLayout>
  );
}
