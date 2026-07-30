"use client"

import React, { useState, use } from "react"
import { useRouter } from "next/navigation"
import { GitBranch } from "lucide-react"
import { GlassPanel } from "@/components/ui/GlassPanel"
import { Button } from "@/components/ui/Button"
import { Input } from "@/components/ui/Input"
import { Alert } from "@/components/ui/Alert"
import { FormField } from "@/components/ui/FormField"
import { knowledgeApi } from "@/lib/api"


export default function ConnectRepositoryPage({ params }: { params: Promise<{ id: string; workspaceId: string }> }) {
  const resolvedParams = use(params)
  const router = useRouter()
  
  const [provider, setProvider] = useState("github")
  const [repository, setRepository] = useState("")
  const [branch, setBranch] = useState("main")
  
  const [isConnecting, setIsConnecting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  const handleConnect = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!repository.trim() || !branch.trim()) return

    setIsConnecting(true)
    setError(null)

    try {
      await knowledgeApi.connectRepository(
        resolvedParams.workspaceId,
        provider,
        repository,
        branch
      )
      setSuccess(true)
      setTimeout(() => {
        router.push(`/organizations/${resolvedParams.id}/workspaces/${resolvedParams.workspaceId}/knowledge/jobs`)
      }, 1500)
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : "Failed to connect repository"
      setError(errorMessage)
    } finally {
      setIsConnecting(false)
    }
  }

  return (
    <div className="max-w-xl mx-auto space-y-6">
      <GlassPanel className="p-8">
        <div className="text-center mb-8">
          <div className="w-12 h-12 rounded-full bg-[rgba(255,255,255,0.05)] flex items-center justify-center mx-auto mb-4 border border-[rgba(255,255,255,0.1)]">
            <GitBranch className="w-6 h-6 text-[var(--color-text-primary)]" />
          </div>
          <h2 className="text-xl font-bold mb-2">Connect Repository</h2>
          <p className="text-sm text-[var(--color-text-secondary)]">
            Index your codebase so Atlas AI can write, refactor, and debug your code with full context.
          </p>
        </div>

        <form onSubmit={handleConnect} className="space-y-4">
          <FormField label="Provider">
            <select 
              value={provider}
              onChange={(e) => setProvider(e.target.value)}
              className="w-full h-10 bg-[rgba(0,0,0,0.2)] border border-[var(--color-border-subtle)] rounded-[var(--radius-sm)] px-3 text-sm focus:outline-none focus:border-[var(--color-primary-base)] transition-colors"
            >
              <option value="github">GitHub</option>
              <option value="gitlab" disabled>GitLab (Coming Soon)</option>
              <option value="azure" disabled>Azure DevOps (Coming Soon)</option>
            </select>
          </FormField>

          <FormField label="Repository Path" required>
            <Input 
              placeholder="e.g. facebook/react"
              value={repository}
              onChange={(e) => setRepository(e.target.value)}
              required
            />
          </FormField>

          <FormField label="Default Branch" required>
            <Input 
              placeholder="main"
              value={branch}
              onChange={(e) => setBranch(e.target.value)}
              required
            />
          </FormField>

          {error && (
            <Alert variant="error">
              {error}
            </Alert>
          )}
          
          {success && (
            <Alert variant="success">
              Repository connected! Starting index...
            </Alert>
          )}

          <div className="pt-4">
            <Button type="submit" variant="primary" className="w-full" disabled={isConnecting}>
              {isConnecting ? <span className="spinner-ring" /> : "Connect & Index"}
            </Button>
          </div>
        </form>
      </GlassPanel>
    </div>
  )
}
