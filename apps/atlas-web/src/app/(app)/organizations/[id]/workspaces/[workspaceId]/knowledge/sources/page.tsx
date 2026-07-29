"use client"

import React, { useEffect, useState, use } from "react"
import { File, Trash2, RefreshCw } from "lucide-react"
import { GlassPanel } from "@/components/ui/GlassPanel"
import { Button } from "@/components/ui/Button"
import { knowledgeApi, KnowledgeSource } from "@/lib/api"
import { getAccessToken } from "@/lib/auth"

export default function KnowledgeSourcesPage({ params }: { params: Promise<{ id: string; workspaceId: string }> }) {
  const resolvedParams = use(params)
  const [sources, setSources] = useState<KnowledgeSource[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const fetchSources = async () => {
    const token = getAccessToken()
    if (!token) return
    try {
      const data = await knowledgeApi.listSources(token, resolvedParams.workspaceId)
      setSources(data)
    } catch (err) {
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchSources()
  }, [resolvedParams.workspaceId])

  const handleDelete = async (sourceId: string) => {
    const token = getAccessToken()
    if (!token || !confirm("Delete this source?")) return
    try {
      await knowledgeApi.deleteSource(token, sourceId)
      setSources(s => s.filter(x => x.id !== sourceId))
    } catch (err) {
      console.error(err)
    }
  }

  const getStatusColor = (status: string) => {
    switch(status) {
      case "ready": return "text-[var(--color-accent-green)] bg-[rgba(34,197,94,0.1)] border-[rgba(34,197,94,0.3)]"
      case "indexing": return "text-[var(--color-accent-blue)] bg-[rgba(59,130,246,0.1)] border-[rgba(59,130,246,0.3)]"
      case "failed": return "text-[var(--color-accent-red)] bg-[rgba(239,68,68,0.1)] border-[rgba(239,68,68,0.3)]"
      default: return "text-[var(--color-text-secondary)] bg-[rgba(255,255,255,0.05)] border-[rgba(255,255,255,0.1)]"
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-lg font-bold">Knowledge Sources</h2>
        <Button variant="secondary" size="sm" onClick={fetchSources} className="gap-2">
          <RefreshCw className="w-3.5 h-3.5" /> Refresh
        </Button>
      </div>

      <GlassPanel>
        {isLoading ? (
          <div className="p-8 text-center text-[var(--color-text-muted)]">Loading sources...</div>
        ) : sources.length === 0 ? (
          <div className="p-8 text-center text-[var(--color-text-muted)]">No sources uploaded yet.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-[var(--color-border-subtle)] text-[11px] uppercase tracking-wider text-[var(--color-text-muted)]">
                  <th className="px-6 py-4 font-medium">Name</th>
                  <th className="px-6 py-4 font-medium">Type</th>
                  <th className="px-6 py-4 font-medium">Status</th>
                  <th className="px-6 py-4 font-medium">Date</th>
                  <th className="px-6 py-4 font-medium text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--color-border-subtle)]">
                {sources.map(source => (
                  <tr key={source.id} className="hover:bg-[rgba(255,255,255,0.02)] transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <File className="w-4 h-4 text-[var(--color-primary-light)]" />
                        <span className="text-sm font-medium">{source.name}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-[var(--color-text-secondary)] capitalize">
                      {source.source_type}
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-0.5 rounded text-xs border font-medium uppercase tracking-wider ${getStatusColor(source.status)}`}>
                        {source.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-[var(--color-text-secondary)]">
                      {new Date(source.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <Button variant="ghost" size="icon" onClick={() => handleDelete(source.id)} className="text-[var(--color-accent-red)] hover:text-red-400">
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </GlassPanel>
    </div>
  )
}
