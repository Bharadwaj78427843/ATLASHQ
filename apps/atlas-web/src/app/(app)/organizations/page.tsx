"use client";

import React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useOrganizations, OrganizationCard } from "@/features/organizations";
import { PageHeader } from "@/components/ui/PageHeader";
import { EmptyState } from "@/components/ui/EmptyState";
import { Button } from "@/components/ui/Button";
import { PageLayout } from "@/components/layout/PageLayout";
import { Building2 } from "lucide-react";

export default function OrganizationsListPage() {
  const router = useRouter();
  const { data, isLoading, error } = useOrganizations("mine");

  return (
    <PageLayout>
      <PageHeader 
        title="Organizations" 
        subtitle="Browse all active organizations on Atlas."
      >
        <Link href="/organizations/new">
          <Button variant="primary">New Organization</Button>
        </Link>
      </PageHeader>

      {error && (
        <div className="alert alert-error" role="alert">
          {error}
        </div>
      )}

      {isLoading ? (
        <div className="flex justify-center py-16">
          <span className="spinner-ring" />
        </div>
      ) : data?.items.length === 0 ? (
        <EmptyState 
          icon={Building2} 
          title="No organizations found" 
          description="Get started by creating your first organization."
          actionLabel="Create Organization"
          onAction={() => router.push("/organizations/new")}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {data?.items.map((org) => (
            <OrganizationCard key={org.id} organization={org} />
          ))}
        </div>
      )}
    </PageLayout>
  );
}
