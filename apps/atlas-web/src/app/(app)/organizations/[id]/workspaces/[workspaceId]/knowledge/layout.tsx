"use client"

import React, { use } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"

export default function KnowledgeLayout({
  children,
  params
}: {
  children: React.ReactNode
  params: Promise<{ id: string; workspaceId: string }>
}) {
  const resolvedParams = use(params)
  const pathname = usePathname()
  const basePath = `/organizations/${resolvedParams.id}/workspaces/${resolvedParams.workspaceId}/knowledge`

  const tabs = [
    { name: "Search", href: basePath },
    { name: "Sources", href: `${basePath}/sources` },
    { name: "Upload", href: `${basePath}/upload` },
    { name: "Connect Repo", href: `${basePath}/repositories` },
    { name: "Index Jobs", href: `${basePath}/jobs` },
  ]

  return (
    <div className="flex-1 flex flex-col h-full bg-[var(--color-background)] text-[var(--color-text-primary)]">
      {/* Header */}
      <div className="p-6 border-b border-[var(--color-border-subtle)] bg-[var(--color-panel)] shrink-0">
        <h1 className="text-2xl font-bold mb-2">Knowledge Hub</h1>
        <p className="text-sm text-[var(--color-text-secondary)] mb-6">
          Manage the context documents and files that Atlas AI uses to understand your workspace.
        </p>

        <div className="flex gap-1 border-b border-[var(--color-border-subtle)]">
          {tabs.map((tab) => {
            const isActive = pathname === tab.href
            return (
              <Link
                key={tab.name}
                href={tab.href}
                className={cn(
                  "px-4 py-2 text-sm font-medium border-b-2 transition-colors",
                  isActive 
                    ? "border-[var(--color-primary-base)] text-[var(--color-primary-base)]" 
                    : "border-transparent text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] hover:border-[var(--color-border-subtle)]"
                )}
              >
                {tab.name}
              </Link>
            )
          })}
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto p-6 relative">
        {/* Decorative background glow */}
        <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-[rgba(124,58,237,0.05)] blur-[120px] rounded-full pointer-events-none" />
        
        <div className="max-w-5xl mx-auto relative z-10">
          {children}
        </div>
      </div>
    </div>
  )
}
