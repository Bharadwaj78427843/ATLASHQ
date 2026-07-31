"use client"

import React, { useCallback, useEffect, useMemo, useState, use } from "react"
import { GitBranch, RefreshCw, Trash2 } from "lucide-react"
import { GlassPanel } from "@/components/ui/GlassPanel"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { Alert } from "@/components/ui/Alert"
import { FormField } from "@/components/ui/FormField"
import { EmptyState } from "@/components/ui/EmptyState"
import { ErrorState } from "@/components/ui/ErrorState"
import { SkeletonLoader } from "@/components/ui/SkeletonLoader"
import { StatusBadge, type StatusType } from "@/components/ui/StatusBadge"
import { ConfirmDialog } from "@/components/ui/ConfirmDialog"
import { ApiError, knowledgeApi, type KnowledgeSource } from "@/lib/api"

type RepositoryMetadata = {
  repository_url?: string
  last_sync?: string
  languages?: Record<string, number>
  frameworks?: string[]
  package_managers?: string[]
  statistics?: {
    file_count?: number
    total_size_bytes?: number
  }
  directory_summary?: {
    folder_count?: number
  }
}

const STATUS_STYLE: Record<string, { label: string; status: StatusType }> = {
  registered: { label: "REGISTERED", status: "neutral" },
  validating: { label: "VALIDATING", status: "warning" },
  cloning: { label: "CLONING", status: "info" },
  indexing: { label: "INDEXING", status: "info" },
  ready: { label: "READY", status: "success" },
  failed: { label: "FAILED", status: "error" },
}

const TRANSIENT_STATUSES = new Set(["registered", "validating", "cloning", "indexing"])

function parseRepositoryMetadata(source: KnowledgeSource): RepositoryMetadata {
  if (!source.metadata_json || typeof source.metadata_json !== "object") {
    return {}
  }

  return source.metadata_json as RepositoryMetadata
}

function formatCount(value: number | undefined): string {
  if (typeof value !== "number" || Number.isNaN(value)) {
    return "-"
  }
  return value.toLocaleString()
}

function formatBytes(value: number | undefined): string {
  if (typeof value !== "number" || Number.isNaN(value) || value <= 0) {
    return "-"
  }

  const units = ["B", "KB", "MB", "GB", "TB"]
  let size = value
  let unitIndex = 0
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex += 1
  }

  const precision = size >= 100 ? 0 : size >= 10 ? 1 : 2
  return `${size.toFixed(precision)} ${units[unitIndex]}`
}

function formatDate(value?: string): string {
  if (!value) {
    return "-"
  }

  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return "-"
  }
  return date.toLocaleString()
}

function isValidGithubUrl(value: string): boolean {
  try {
    const url = new URL(value)
    const isHttps = url.protocol === "https:"
    const isGitHubHost = url.hostname === "github.com" || url.hostname === "www.github.com"
    const segments = url.pathname.split("/").filter(Boolean)
    return isHttps && isGitHubHost && segments.length >= 2
  } catch {
    return false
  }
}

function mapUserFriendlyError(err: unknown): string {
  const fallback = "Unable to complete this repository request right now. Please try again."
  if (!(err instanceof Error)) {
    return fallback
  }

  if (err instanceof ApiError) {
    const detail = err.detail.toLowerCase()
    if (err.status === 400 && detail.includes("url")) {
      return "Invalid GitHub URL. Please use a full URL like https://github.com/owner/repository."
    }
    if (err.status === 404 || detail.includes("not found")) {
      return "Repository not found. Confirm the repository exists and that Atlas has access."
    }
    if (err.status === 409 && detail.includes("already in progress")) {
      return "Repository is already syncing. Please wait for the current sync to finish."
    }
    if (err.status === 409 || detail.includes("already exists")) {
      return "Repository already exists in this workspace."
    }
    if (err.status >= 500) {
      return "The backend is currently unavailable. Please try again shortly."
    }
    if (detail.includes("timeout")) {
      return "The request timed out. Please retry in a moment."
    }
    return err.detail
  }

  const message = err.message.toLowerCase()
  if (message.includes("failed to fetch") || message.includes("network")) {
    return "Network error or backend offline. Check your connection and try again."
  }
  if (message.includes("timeout")) {
    return "The request timed out. Please retry in a moment."
  }

  return fallback
}

function RepositoryCard({
  source,
  syncing,
  deleting,
  onSync,
  onDelete,
}: {
  source: KnowledgeSource
  syncing: boolean
  deleting: boolean
  onSync: (sourceId: string) => Promise<void>
  onDelete: (sourceId: string) => Promise<void>
}) {
  const statusKey = source.status.toLowerCase()
  const status = STATUS_STYLE[statusKey] ?? { label: source.status.toUpperCase(), status: "neutral" as const }
  const metadata = parseRepositoryMetadata(source)

  const languageLabels = Object.keys(metadata.languages ?? {})
  const frameworkLabels = metadata.frameworks ?? []
  const packageManagerLabels = metadata.package_managers ?? []

  const lastSync = formatDate(metadata.last_sync)
  const fileCount = formatCount(metadata.statistics?.file_count)
  const folderCount = formatCount(metadata.directory_summary?.folder_count)
  const repositorySize = formatBytes(metadata.statistics?.total_size_bytes ?? source.size_bytes ?? undefined)

  const syncDisabled = syncing || deleting || TRANSIENT_STATUSES.has(statusKey)

  return (
    <GlassPanel className="p-5 space-y-4">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <h3 className="text-base font-semibold text-[var(--color-text-primary)] truncate">{source.name}</h3>
          <a
            href={metadata.repository_url}
            target="_blank"
            rel="noreferrer"
            className="text-xs text-[var(--color-primary-light)] hover:underline break-all"
          >
            {metadata.repository_url || "GitHub URL unavailable"}
          </a>
        </div>
        <StatusBadge status={status.status} label={status.label} />
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
        <div className="rounded-[var(--radius-sm)] border border-[var(--color-border-subtle)] bg-[rgba(255,255,255,0.02)] p-3">
          <p className="text-[var(--color-text-muted)] mb-1">File Count</p>
          <p className="text-sm font-medium text-[var(--color-text-primary)]">{fileCount}</p>
        </div>
        <div className="rounded-[var(--radius-sm)] border border-[var(--color-border-subtle)] bg-[rgba(255,255,255,0.02)] p-3">
          <p className="text-[var(--color-text-muted)] mb-1">Folder Count</p>
          <p className="text-sm font-medium text-[var(--color-text-primary)]">{folderCount}</p>
        </div>
        <div className="rounded-[var(--radius-sm)] border border-[var(--color-border-subtle)] bg-[rgba(255,255,255,0.02)] p-3">
          <p className="text-[var(--color-text-muted)] mb-1">Last Sync</p>
          <p className="text-sm font-medium text-[var(--color-text-primary)]">{lastSync}</p>
        </div>
        <div className="rounded-[var(--radius-sm)] border border-[var(--color-border-subtle)] bg-[rgba(255,255,255,0.02)] p-3">
          <p className="text-[var(--color-text-muted)] mb-1">Repository Size</p>
          <p className="text-sm font-medium text-[var(--color-text-primary)]">{repositorySize}</p>
        </div>
      </div>

      <div className="space-y-2">
        <p className="text-xs text-[var(--color-text-muted)]">Languages</p>
        <p className="text-sm text-[var(--color-text-secondary)]">{languageLabels.length > 0 ? languageLabels.join(", ") : "-"}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div className="space-y-2">
          <p className="text-xs text-[var(--color-text-muted)]">Frameworks</p>
          <p className="text-sm text-[var(--color-text-secondary)]">{frameworkLabels.length > 0 ? frameworkLabels.join(", ") : "-"}</p>
        </div>
        <div className="space-y-2">
          <p className="text-xs text-[var(--color-text-muted)]">Package Managers</p>
          <p className="text-sm text-[var(--color-text-secondary)]">{packageManagerLabels.length > 0 ? packageManagerLabels.join(", ") : "-"}</p>
        </div>
      </div>

      <div className="flex justify-end gap-2">
        <Button
          variant="danger"
          size="sm"
          className="gap-2"
          disabled={syncDisabled}
          onClick={() => void onDelete(source.id)}
        >
          {deleting ? <span className="spinner-ring" aria-label="Deleting repository" /> : <Trash2 className="w-3.5 h-3.5" />}
          Delete
        </Button>
        <Button
          variant="secondary"
          size="sm"
          className="gap-2"
          disabled={syncDisabled}
          onClick={() => void onSync(source.id)}
        >
          {syncing ? <span className="spinner-ring" aria-label="Syncing repository" /> : <RefreshCw className="w-3.5 h-3.5" />}
          Sync
        </Button>
      </div>
    </GlassPanel>
  )
}

function RepositoryCardSkeleton() {
  return (
    <GlassPanel className="p-5 space-y-4">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <SkeletonLoader lines={2} />
        </div>
        <div className="w-28">
          <SkeletonLoader lines={1} />
        </div>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {Array.from({ length: 4 }).map((_, idx) => (
          <div key={idx} className="rounded-[var(--radius-sm)] border border-[var(--color-border-subtle)] bg-[rgba(255,255,255,0.02)] p-3">
            <SkeletonLoader lines={2} />
          </div>
        ))}
      </div>
      <SkeletonLoader lines={1} />
      <SkeletonLoader lines={1} />
    </GlassPanel>
  )
}

export default function ConnectRepositoryPage({ params }: { params: Promise<{ id: string; workspaceId: string }> }) {
  const resolvedParams = use(params)
  const [repositoryUrl, setRepositoryUrl] = useState("")
  const [branch, setBranch] = useState("main")

  const [repositories, setRepositories] = useState<KnowledgeSource[]>([])
  const [isLoadingRepositories, setIsLoadingRepositories] = useState(true)

  const [isConnecting, setIsConnecting] = useState(false)
  const [syncingRepositoryIds, setSyncingRepositoryIds] = useState<Record<string, boolean>>({})
  const [deletingRepositoryIds, setDeletingRepositoryIds] = useState<Record<string, boolean>>({})
  const [pendingDeleteSourceId, setPendingDeleteSourceId] = useState<string | null>(null)

  const [error, setError] = useState<string | null>(null)
  const [pageError, setPageError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  const fetchRepositories = useCallback(async () => {
    try {
      setPageError(null)
      setIsLoadingRepositories(true)
      const allSources = await knowledgeApi.listSources(resolvedParams.workspaceId)
      const repositorySources = allSources
        .filter((source) => source.source_type.toLowerCase() === "repository")
        .sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())
      setRepositories(repositorySources)
    } catch (err: unknown) {
      setPageError(mapUserFriendlyError(err))
    } finally {
      setIsLoadingRepositories(false)
    }
  }, [resolvedParams.workspaceId])

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void fetchRepositories()
  }, [fetchRepositories])

  const shouldPoll = useMemo(() => {
    return repositories.some((repo) => TRANSIENT_STATUSES.has(repo.status.toLowerCase()))
  }, [repositories])

  useEffect(() => {
    if (!shouldPoll) {
      return
    }

    const interval = setInterval(() => {
      void fetchRepositories()
    }, 4000)

    return () => clearInterval(interval)
  }, [fetchRepositories, shouldPoll])

  const handleConnect = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!repositoryUrl.trim() || !branch.trim()) {
      return
    }

    if (!isValidGithubUrl(repositoryUrl.trim())) {
      setError("Invalid GitHub URL. Use a full URL like https://github.com/owner/repository.")
      return
    }

    setIsConnecting(true)
    setError(null)
    setSuccessMessage(null)

    try {
      const connected = await knowledgeApi.connectRepository(
        resolvedParams.workspaceId,
        "github",
        repositoryUrl.trim(),
        branch
      )

      setRepositories((prev) => {
        const withoutExisting = prev.filter((repo) => repo.id !== connected.id)
        return [connected, ...withoutExisting]
      })

      setRepositoryUrl("")
      setBranch("main")
      setSuccessMessage("Repository connected. Cloning and indexing has started.")

      // Refresh once to ensure we display the latest metadata and status.
      await fetchRepositories()
    } catch (err: unknown) {
      setError(mapUserFriendlyError(err))
    } finally {
      setIsConnecting(false)
    }
  }

  const handleSync = async (sourceId: string) => {
    setError(null)
    setSuccessMessage(null)
    setSyncingRepositoryIds((prev) => ({ ...prev, [sourceId]: true }))

    try {
      const updated = await knowledgeApi.syncRepository(sourceId)
      setRepositories((prev) => prev.map((repo) => (repo.id === sourceId ? updated : repo)))
      setSuccessMessage("Repository sync started. Metadata will refresh automatically.")
      await fetchRepositories()
    } catch (err: unknown) {
      setError(mapUserFriendlyError(err))
    } finally {
      setSyncingRepositoryIds((prev) => {
        const next = { ...prev }
        delete next[sourceId]
        return next
      })
    }
  }

  const handleDelete = async (sourceId: string) => {
    setError(null)
    setSuccessMessage(null)
    setDeletingRepositoryIds((prev) => ({ ...prev, [sourceId]: true }))

    try {
      await knowledgeApi.deleteSource(sourceId)
      setRepositories((prev) => prev.filter((repo) => repo.id !== sourceId))
      setSuccessMessage("Repository removed successfully.")
    } catch (err: unknown) {
      setError(mapUserFriendlyError(err))
    } finally {
      setDeletingRepositoryIds((prev) => {
        const next = { ...prev }
        delete next[sourceId]
        return next
      })
      setPendingDeleteSourceId(null)
    }
  }

  const pendingDeleteRepository = pendingDeleteSourceId
    ? repositories.find((repository) => repository.id === pendingDeleteSourceId) ?? null
    : null

  return (
    <div className="space-y-6">
      <GlassPanel className="p-8">
        <div className="text-center mb-6">
          <div className="w-12 h-12 rounded-full bg-[rgba(255,255,255,0.05)] flex items-center justify-center mx-auto mb-4 border border-[rgba(255,255,255,0.1)]">
            <GitBranch className="w-6 h-6 text-[var(--color-text-primary)]" />
          </div>
          <h2 className="text-xl font-bold mb-2">Connect Repository</h2>
          <p className="text-sm text-[var(--color-text-secondary)]">
            Paste a GitHub repository URL to connect it to your Knowledge Hub.
          </p>
        </div>

        <form onSubmit={handleConnect} className="grid grid-cols-1 lg:grid-cols-12 gap-3">
          <div className="lg:col-span-8">
            <FormField label="GitHub URL" required>
              <Input
                placeholder="https://github.com/owner/repository"
                value={repositoryUrl}
                onChange={(e) => setRepositoryUrl(e.target.value)}
                required
              />
            </FormField>
          </div>

          <div className="lg:col-span-2">
            <FormField label="Branch" required>
              <Input
                placeholder="main"
                value={branch}
                onChange={(e) => setBranch(e.target.value)}
                required
              />
            </FormField>
          </div>

          <div className="lg:col-span-2 flex items-end">
            <Button type="submit" variant="primary" className="w-full" disabled={isConnecting}>
              {isConnecting ? <span className="spinner-ring" aria-label="Connecting repository" /> : "Connect"}
            </Button>
          </div>
        </form>

        {(error || successMessage) && (
          <div className="mt-4">
            {error ? <Alert variant="error">{error}</Alert> : null}
            {successMessage ? <Alert variant="success">{successMessage}</Alert> : null}
          </div>
        )}
      </GlassPanel>

      <div className="space-y-4">
        <div className="flex items-center justify-between gap-3">
          <h2 className="text-lg font-semibold">Connected Repositories</h2>
          <Button variant="secondary" size="sm" className="gap-2" onClick={() => void fetchRepositories()} disabled={isLoadingRepositories}>
            <RefreshCw className="w-3.5 h-3.5" />
            Refresh
          </Button>
        </div>

        {pageError ? (
          <ErrorState title="Unable to load repositories" error={pageError} onRetry={() => void fetchRepositories()} />
        ) : null}

        {!pageError && isLoadingRepositories ? (
          <div className="space-y-4">
            <RepositoryCardSkeleton />
            <RepositoryCardSkeleton />
          </div>
        ) : null}

        {!pageError && !isLoadingRepositories && repositories.length === 0 ? (
          <EmptyState
            icon={GitBranch}
            title="No repositories connected yet."
            description="Connect your first GitHub repository to begin building your Knowledge Hub."
          />
        ) : null}

        {!pageError && !isLoadingRepositories && repositories.length > 0 ? (
          <div className="space-y-4">
            {repositories.map((source) => (
              <RepositoryCard
                key={source.id}
                source={source}
                syncing={Boolean(syncingRepositoryIds[source.id])}
                deleting={Boolean(deletingRepositoryIds[source.id])}
                onSync={handleSync}
                onDelete={async (sourceId) => {
                  setPendingDeleteSourceId(sourceId)
                }}
              />
            ))}
          </div>
        ) : null}
      </div>

      <ConfirmDialog
        isOpen={Boolean(pendingDeleteRepository)}
        title="Delete Repository"
        description={
          pendingDeleteRepository
            ? `Delete repository source \"${pendingDeleteRepository.name}\" from this workspace?`
            : "Delete repository source from this workspace?"
        }
        confirmLabel="Delete"
        cancelLabel="Cancel"
        isDestructive
        isLoading={Boolean(pendingDeleteSourceId && deletingRepositoryIds[pendingDeleteSourceId])}
        onCancel={() => setPendingDeleteSourceId(null)}
        onConfirm={() => {
          if (pendingDeleteSourceId) {
            void handleDelete(pendingDeleteSourceId)
          }
        }}
      />
    </div>
  )
}
