"use client"

import React, { useEffect, useState, use } from "react"
import { Activity, RefreshCw } from "lucide-react"
import { GlassPanel } from "@/components/ui/GlassPanel"
import { Button } from "@/components/ui/Button"
import { knowledgeApi, IndexJob, KnowledgeSource } from "@/lib/api"
import { getAccessToken } from "@/lib/auth"

export default function KnowledgeJobsPage({ params }: { params: Promise<{ id: string; workspaceId: string }> }) {
  const resolvedParams = use(params)
  const [sources, setSources] = useState<KnowledgeSource[]>([])
  const [jobs, setJobs] = useState<IndexJob[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const fetchData = async () => {
    const token = getAccessToken()
    if (!token) return
    try {
      // Fetch all sources first to get their IDs
      const sourceData = await knowledgeApi.listSources(token, resolvedParams.workspaceId)
      setSources(sourceData)
      
      // Fetch jobs for each source
      let allJobs: IndexJob[] = []
      for (const s of sourceData) {
        const sourceJobs = await knowledgeApi.listJobs(token, s.id)
        allJobs = [...allJobs, ...sourceJobs]
      }
      
      // Sort jobs by started_at descending
      allJobs.sort((a, b) => new Date(b.started_at || 0).getTime() - new Date(a.started_at || 0).getTime())
      setJobs(allJobs)
    } catch (err) {
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [resolvedParams.workspaceId])

  const getStatusColor = (status: string) => {
    switch(status) {
      case "completed": return "text-[var(--color-accent-green)]"
      case "running": return "text-[var(--color-accent-blue)]"
      case "failed": return "text-[var(--color-accent-red)]"
      default: return "text-[var(--color-text-secondary)]"
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-lg font-bold">Indexing Jobs</h2>
        <Button variant="secondary" size="sm" onClick={fetchData} className="gap-2">
          <RefreshCw className="w-3.5 h-3.5" /> Refresh
        </Button>
      </div>

      <GlassPanel>
        {isLoading ? (
          <div className="p-8 text-center text-[var(--color-text-muted)]">Loading jobs...</div>
        ) : jobs.length === 0 ? (
          <div className="p-8 text-center text-[var(--color-text-muted)]">No indexing jobs found.</div>
        ) : (
          <div className="p-2">
            {jobs.map(job => {
              const source = sources.find(s => s.id === job.source_id)
              return (
                <div key={job.id} className="p-4 border-b border-[var(--color-border-subtle)] last:border-0 hover:bg-[rgba(255,255,255,0.02)] transition-colors">
                  <div className="flex justify-between items-start mb-3">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded bg-[rgba(255,255,255,0.05)] flex items-center justify-center">
                        <Activity className="w-4 h-4 text-[var(--color-primary-light)]" />
                      </div>
                      <div>
                        <p className="text-sm font-medium">{source?.name || 'Unknown Source'}</p>
                        <p className="text-[10px] text-[var(--color-text-muted)] font-mono">{job.id}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <span className={`text-xs font-semibold uppercase tracking-wider ${getStatusColor(job.status)}`}>
                        {job.status}
                      </span>
                      <p className="text-[10px] text-[var(--color-text-muted)] mt-1">
                        {new Date(job.started_at || '').toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                  
                  {/* Progress Bar */}
                  <div className="w-full bg-[rgba(255,255,255,0.05)] h-1.5 rounded-full overflow-hidden">
                    <div 
                      className={`h-full rounded-full transition-all duration-500 ${job.status === 'failed' ? 'bg-[var(--color-accent-red)]' : 'bg-[var(--color-primary-base)]'}`} 
                      style={{ width: `${Math.max(job.progress * 100, 2)}%` }} 
                    />
                  </div>
                  
                  {job.error_message && (
                    <p className="mt-2 text-xs text-[var(--color-accent-red)] bg-[rgba(239,68,68,0.1)] p-2 rounded">
                      {job.error_message}
                    </p>
                  )}
                </div>
              )
            })}
          </div>
        )}
      </GlassPanel>
    </div>
  )
}
