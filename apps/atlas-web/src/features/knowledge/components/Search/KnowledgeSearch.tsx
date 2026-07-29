import React, { useState } from "react"
import { Search, Database, FileText } from "lucide-react"
import { GlassPanel } from "@/components/ui/GlassPanel"
import { Input } from "@/components/ui/Input"
import { Button } from "@/components/ui/Button"
import { useKnowledge } from "../../hooks/useKnowledge"
import { SearchResultSnippet } from "../../types"

export function KnowledgeSearch({ workspaceId, projectId }: { workspaceId: string, projectId?: string }) {
  const { search } = useKnowledge(workspaceId, projectId)
  const [query, setQuery] = useState("")
  const [results, setResults] = useState<SearchResultSnippet[]>([])
  const [isLoading, setIsLoading] = useState(false)

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return

    setIsLoading(true)
    try {
      const res = await search(query)
      setResults(res)
    } catch (err) {
      console.error("Search failed", err)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <GlassPanel className="p-8 text-center" glow>
        <div className="w-12 h-12 rounded-full bg-[rgba(124,58,237,0.1)] flex items-center justify-center mx-auto mb-4 border border-[rgba(124,58,237,0.3)]">
          <Database className="w-6 h-6 text-[var(--color-primary-light)]" />
        </div>
        <h2 className="text-xl font-bold mb-2">Search Workspace Knowledge</h2>
        <p className="text-sm text-[var(--color-text-secondary)] mb-6 max-w-lg mx-auto">
          Query indexed documentation, source code, logs, and files using natural language.
        </p>

        <form onSubmit={handleSearch} className="max-w-2xl mx-auto flex gap-3">
          <Input 
            icon={<Search className="w-4 h-4" />}
            placeholder="E.g., How does the authentication flow work?" 
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="flex-1 h-12 text-base"
          />
          <Button type="submit" size="lg" disabled={isLoading} className="w-32">
            {isLoading ? <span className="spinner-ring" /> : "Search"}
          </Button>
        </form>
      </GlassPanel>

      {results.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-sm font-semibold text-[var(--color-text-secondary)]">Search Results</h3>
          {results.map((res, i) => (
            <GlassPanel key={i} className="p-5">
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <FileText className="w-4 h-4 text-[var(--color-primary-light)]" />
                  <span className="text-sm font-semibold">{res.filename}</span>
                </div>
                <span className="text-[10px] font-mono text-[var(--color-accent-green)] px-2 py-0.5 rounded border border-[rgba(34,197,94,0.3)] bg-[rgba(34,197,94,0.1)]">
                  Score: {res.score.toFixed(2)}
                </span>
              </div>
              <p className="text-sm text-[var(--color-text-secondary)] mt-3 p-3 bg-[rgba(0,0,0,0.2)] rounded border border-[var(--color-border-subtle)] font-mono">
                {res.content}
              </p>
            </GlassPanel>
          ))}
        </div>
      )}
    </div>
  )
}
