import React from "react"
import Link from "next/link"
import { Folder, Globe } from "lucide-react"
import { GlassPanel } from "@/components/ui/GlassPanel"
import { ProjectRead } from "../types"

interface ProjectCardProps {
  organizationId: string
  workspaceId: string
  project: ProjectRead
  environmentCount?: number
}

export function ProjectCard({ organizationId, workspaceId, project, environmentCount }: ProjectCardProps) {
  return (
    <Link href={`/organizations/${organizationId}/workspaces/${workspaceId}/projects/${project.id}`} className="block group">
      <GlassPanel className="p-6 transition-all duration-200 hover:border-[var(--color-primary-base)] hover:shadow-[0_0_20px_rgba(124,58,237,0.15)] h-full flex flex-col">
        <div className="flex items-center gap-4 mb-4">
          <div className="w-12 h-12 rounded-xl bg-[rgba(255,255,255,0.05)] border border-[rgba(255,255,255,0.1)] flex items-center justify-center group-hover:bg-[rgba(124,58,237,0.1)] group-hover:border-[rgba(124,58,237,0.2)] transition-colors">
            <Folder className="w-6 h-6 text-[var(--color-text-primary)] group-hover:text-[var(--color-primary-light)] transition-colors" />
          </div>
          <div>
            <h3 className="font-semibold text-lg text-[var(--color-text-primary)] group-hover:text-white transition-colors">{project.name}</h3>
          </div>
        </div>
        
        {project.description && (
          <p className="text-sm text-[var(--color-text-secondary)] line-clamp-2 mb-4 flex-grow">
            {project.description}
          </p>
        )}
        
        <div className="mt-auto pt-4 border-t border-[rgba(255,255,255,0.05)] flex items-center gap-4 text-xs text-[var(--color-text-muted)]">
          {environmentCount !== undefined && (
            <div className="flex items-center gap-1.5">
              <Globe className="w-3.5 h-3.5" />
              <span>{environmentCount} Environment{environmentCount !== 1 && "s"}</span>
            </div>
          )}
        </div>
      </GlassPanel>
    </Link>
  )
}
