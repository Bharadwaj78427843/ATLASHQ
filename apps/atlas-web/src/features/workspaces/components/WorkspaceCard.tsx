import React from "react"
import Link from "next/link"
import { Briefcase, Folder } from "lucide-react"
import { GlassPanel } from "@/components/ui/GlassPanel"
import { WorkspaceRead } from "../types"

interface WorkspaceCardProps {
  organizationId: string
  workspace: WorkspaceRead
  projectCount?: number
}

export function WorkspaceCard({ organizationId, workspace, projectCount }: WorkspaceCardProps) {
  return (
    <Link href={`/organizations/${organizationId}/workspaces/${workspace.id}`} className="block group">
      <GlassPanel className="p-6 transition-all duration-200 hover:border-[var(--color-primary-base)] hover:shadow-[0_0_20px_rgba(124,58,237,0.15)] h-full flex flex-col">
        <div className="flex items-center gap-4 mb-4">
          <div className="w-12 h-12 rounded-xl bg-[rgba(255,255,255,0.05)] border border-[rgba(255,255,255,0.1)] flex items-center justify-center group-hover:bg-[rgba(124,58,237,0.1)] group-hover:border-[rgba(124,58,237,0.2)] transition-colors">
            <Briefcase className="w-6 h-6 text-[var(--color-text-primary)] group-hover:text-[var(--color-primary-light)] transition-colors" />
          </div>
          <div>
            <h3 className="font-semibold text-lg text-[var(--color-text-primary)] group-hover:text-white transition-colors">{workspace.name}</h3>
            <p className="text-sm text-[var(--color-text-secondary)]">@{workspace.slug}</p>
          </div>
        </div>
        
        {workspace.description && (
          <p className="text-sm text-[var(--color-text-secondary)] line-clamp-2 mb-4 flex-grow">
            {workspace.description}
          </p>
        )}
        
        <div className="mt-auto pt-4 border-t border-[rgba(255,255,255,0.05)] flex items-center gap-4 text-xs text-[var(--color-text-muted)]">
          {projectCount !== undefined && (
            <div className="flex items-center gap-1.5">
              <Folder className="w-3.5 h-3.5" />
              <span>{projectCount} Project{projectCount !== 1 && "s"}</span>
            </div>
          )}
        </div>
      </GlassPanel>
    </Link>
  )
}
