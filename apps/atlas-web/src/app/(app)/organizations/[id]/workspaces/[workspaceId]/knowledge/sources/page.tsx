"use client"

import React, { useEffect, useState, use } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { File, Trash2, RefreshCw } from "lucide-react"
import { GlassPanel } from "@/components/ui/GlassPanel"
import { Button } from "@/components/ui/Button"
import { knowledgeApi, KnowledgeSource } from "@/lib/api"
import { EmptyState } from "@/components/ui/EmptyState"
import { ErrorState } from "@/components/ui/ErrorState"
import { SkeletonLoader } from "@/components/ui/SkeletonLoader"
import { ConfirmDialog } from "@/components/ui/ConfirmDialog"

export default function KnowledgeSourcesPage({ params }: { params: Promise<{ id: string; workspaceId: string }> }) {
  const resolvedParams = use(params)
  const router = useRouter()
  const [sources, setSources] = useState<KnowledgeSource[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [sourceToDelete, setSourceToDelete] = useState<string | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)

  const fetchSources = React.useCallback(async () => {
    try {
      setIsLoading(true)
      setError(null)
      const data = await knowledgeApi.listSources(resolvedParams.workspaceId)
      setSources(data)
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Failed to load knowledge sources"
      setError(message)
    } finally {
      setIsLoading(false)
    }
  }, [resolvedParams.workspaceId])

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void fetchSources()
  }, [fetchSources])

  const handleDelete = async () => {
    if (!sourceToDelete) return
    setIsDeleting(true)
    try {
      await knowledgeApi.deleteSource(sourceToDelete)
      setSources(s => s.filter(x => x.id !== sourceToDelete))
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Failed to delete source"
      setError(message)
    } finally {
      setIsDeleting(false)
      setSourceToDelete(null)
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

      {error ? <ErrorState title="Unable to load sources" error={error} onRetry={() => void fetchSources()} /> : null}

      <GlassPanel>
        {isLoading ? (
          <div className="p-6"><SkeletonLoader lines={5} /></div>
        ) : sources.length === 0 ? (
          <EmptyState
            icon={File}
            title="No knowledge sources yet"
            description="Upload your first document or connect a repository to start indexing workspace knowledge."
            actionLabel="Upload Document"
            onAction={() => router.push(`/organizations/${resolvedParams.id}/workspaces/${resolvedParams.workspaceId}/knowledge/upload`)}
          />
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
                      <Button variant="ghost" size="icon" onClick={() => setSourceToDelete(source.id)} className="text-[var(--color-accent-red)] hover:text-red-400">
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

      {!isLoading && sources.length === 0 ? (
        <div className="flex justify-center">
          <Link href={`/organizations/${resolvedParams.id}/workspaces/${resolvedParams.workspaceId}/knowledge/repositories`}>
            <Button variant="secondary">Connect Repository Instead</Button>
          </Link>
        </div>
      ) : null}

      <ConfirmDialog
        isOpen={!!sourceToDelete}
        title="Delete Knowledge Source"
        description="Are you sure you want to delete this knowledge source? This action cannot be undone."
        confirmLabel="Delete"
        cancelLabel="Cancel"
        isDestructive
        isLoading={isDeleting}
        onCancel={() => setSourceToDelete(null)}
        onConfirm={handleDelete}
      />
    </div>
  )
}
