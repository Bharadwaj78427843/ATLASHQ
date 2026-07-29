"use client"

import React, { useState, use } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { BookOpen, Upload, GitBranch, Activity, Search } from "lucide-react"
import { PageHeader } from "@/components/ui/PageHeader"
import { PageLayout } from "@/components/layout/PageLayout"
import { KnowledgeSearch } from "@/features/knowledge"

const TABS = [
  { id: "search", label: "Search", icon: Search },
  { id: "sources", label: "Sources", icon: BookOpen },
  { id: "upload", label: "Upload", icon: Upload },
  { id: "repositories", label: "Repositories", icon: GitBranch },
  { id: "jobs", label: "Index Jobs", icon: Activity },
]

export default function WorkspaceKnowledgePage({ params }: { params: Promise<{ id: string; workspaceId: string }> }) {
  const resolvedParams = use(params)
  const { id: orgId, workspaceId } = resolvedParams
  const router = useRouter()
  const [activeTab, setActiveTab] = useState("search")

  const baseUrl = `/organizations/${orgId}/workspaces/${workspaceId}/knowledge`

  return (
    <PageLayout maxWidth="5xl">
      <PageHeader
        title="Knowledge Hub"
        subtitle="Search, upload, and manage knowledge sources for your workspace."
        backLink={{ href: `/organizations/${orgId}/workspaces/${workspaceId}`, label: "Back to Workspace" }}
      />

      {/* Tab Navigation */}
      <div className="flex gap-1 mb-8 border-b border-[var(--color-border-subtle)]">
        {TABS.map(tab => (
          <button
            key={tab.id}
            onClick={() => {
              if (tab.id === "sources") {
                router.push(`${baseUrl}/sources`)
              } else if (tab.id === "upload") {
                router.push(`${baseUrl}/upload`)
              } else if (tab.id === "repositories") {
                router.push(`${baseUrl}/repositories`)
              } else if (tab.id === "jobs") {
                router.push(`${baseUrl}/jobs`)
              } else {
                setActiveTab(tab.id)
              }
            }}
            className={`flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors border-b-2 -mb-px ${
              activeTab === tab.id
                ? "border-[var(--color-primary-base)] text-[var(--color-primary-light)]"
                : "border-transparent text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
            }`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Quick Action Buttons */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-8">
        <Link
          href={`${baseUrl}/upload`}
          className="flex flex-col items-center gap-2 p-4 bg-[var(--color-panel)] border border-[var(--color-border-subtle)] rounded-[var(--radius-md)] hover:border-[var(--color-primary-base)] hover:bg-[rgba(124,58,237,0.05)] transition-all group"
        >
          <Upload className="w-5 h-5 text-[var(--color-text-muted)] group-hover:text-[var(--color-primary-light)]" />
          <span className="text-xs font-medium text-[var(--color-text-secondary)] group-hover:text-[var(--color-text-primary)]">Upload Doc</span>
        </Link>
        <Link
          href={`${baseUrl}/repositories`}
          className="flex flex-col items-center gap-2 p-4 bg-[var(--color-panel)] border border-[var(--color-border-subtle)] rounded-[var(--radius-md)] hover:border-[var(--color-primary-base)] hover:bg-[rgba(124,58,237,0.05)] transition-all group"
        >
          <GitBranch className="w-5 h-5 text-[var(--color-text-muted)] group-hover:text-[var(--color-primary-light)]" />
          <span className="text-xs font-medium text-[var(--color-text-secondary)] group-hover:text-[var(--color-text-primary)]">Connect Repo</span>
        </Link>
        <Link
          href={`${baseUrl}/sources`}
          className="flex flex-col items-center gap-2 p-4 bg-[var(--color-panel)] border border-[var(--color-border-subtle)] rounded-[var(--radius-md)] hover:border-[var(--color-primary-base)] hover:bg-[rgba(124,58,237,0.05)] transition-all group"
        >
          <BookOpen className="w-5 h-5 text-[var(--color-text-muted)] group-hover:text-[var(--color-primary-light)]" />
          <span className="text-xs font-medium text-[var(--color-text-secondary)] group-hover:text-[var(--color-text-primary)]">All Sources</span>
        </Link>
        <Link
          href={`${baseUrl}/jobs`}
          className="flex flex-col items-center gap-2 p-4 bg-[var(--color-panel)] border border-[var(--color-border-subtle)] rounded-[var(--radius-md)] hover:border-[var(--color-primary-base)] hover:bg-[rgba(124,58,237,0.05)] transition-all group"
        >
          <Activity className="w-5 h-5 text-[var(--color-text-muted)] group-hover:text-[var(--color-primary-light)]" />
          <span className="text-xs font-medium text-[var(--color-text-secondary)] group-hover:text-[var(--color-text-primary)]">Index Jobs</span>
        </Link>
      </div>

      {/* Search Panel */}
      <KnowledgeSearch workspaceId={workspaceId} />
    </PageLayout>
  )
}
