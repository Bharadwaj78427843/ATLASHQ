import React from "react"
import Link from "next/link"
import { Globe, Server } from "lucide-react"
import { GlassPanel } from "@/components/ui/GlassPanel"
import { EnvironmentRead } from "../types"

interface EnvironmentCardProps {
  organizationId: string
  workspaceId: string
  projectId: string
  environment: EnvironmentRead
}

export function EnvironmentCard({ organizationId, workspaceId, projectId, environment }: EnvironmentCardProps) {
  const getEnvColor = (type: string) => {
    switch (type) {
      case "PRODUCTION": return "bg-red-500/10 border-red-500/20 text-red-400";
      case "STAGING": return "bg-orange-500/10 border-orange-500/20 text-orange-400";
      case "PREVIEW": return "bg-blue-500/10 border-blue-500/20 text-blue-400";
      default: return "bg-green-500/10 border-green-500/20 text-green-400";
    }
  };

  return (
    <Link href={`/organizations/${organizationId}/workspaces/${workspaceId}/projects/${projectId}/environments/${environment.id}`} className="block group">
      <GlassPanel className="p-6 transition-all duration-200 hover:border-[var(--color-primary-base)] hover:shadow-[0_0_20px_rgba(124,58,237,0.15)] h-full flex flex-col">
        <div className="flex items-center gap-4 mb-4">
          <div className={`w-12 h-12 rounded-xl border flex items-center justify-center transition-colors ${getEnvColor(environment.type)} group-hover:bg-[rgba(124,58,237,0.1)] group-hover:border-[rgba(124,58,237,0.2)] group-hover:text-[var(--color-primary-light)]`}>
            <Globe className="w-6 h-6" />
          </div>
          <div>
            <h3 className="font-semibold text-lg text-[var(--color-text-primary)] group-hover:text-white transition-colors">{environment.name}</h3>
            <div className="flex gap-2 mt-1">
              <span className={`text-xs px-2 py-0.5 rounded-full border ${getEnvColor(environment.type)}`}>
                {environment.type}
              </span>
              {!environment.is_active && <span className="text-xs px-2 py-0.5 rounded-full border bg-red-500/10 border-red-500/20 text-red-400">Inactive</span>}
            </div>
          </div>
        </div>
        
        <div className="mt-auto pt-4 border-t border-[rgba(255,255,255,0.05)] flex items-center gap-4 text-xs text-[var(--color-text-muted)]">
          <div className="flex items-center gap-1.5">
            <Server className="w-3.5 h-3.5" />
            <span>ID: {environment.id.substring(0, 8)}...</span>
          </div>
        </div>
      </GlassPanel>
    </Link>
  )
}
