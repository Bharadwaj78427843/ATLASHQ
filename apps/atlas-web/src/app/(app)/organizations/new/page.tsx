"use client";

/**
 * src/app/organizations/new/page.tsx
 *
 * ATLAS-011 — Create Organization page.
 * Form with frontend validation reflecting backend schemas.
 */
import React from "react";
import { PageHeader } from "@/components/ui/PageHeader";
import { PageLayout } from "@/components/layout/PageLayout";
import { OrganizationForm } from "@/features/organizations";

export default function CreateOrganizationPage() {
  return (
    <PageLayout maxWidth="2xl">
      <PageHeader 
        title="Create Organization" 
        subtitle="Set up a new workspace for your team."
        backLink={{ href: "/organizations", label: "Back to Organizations" }}
      />
      <OrganizationForm />
    </PageLayout>
  );
}
