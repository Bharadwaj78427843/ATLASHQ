"use client"

import React, { useState, useRef, use } from "react"
import { useRouter } from "next/navigation"
import { UploadCloud, File, CheckCircle2, AlertCircle } from "lucide-react"
import { GlassPanel } from "@/components/ui/GlassPanel"
import { Button } from "@/components/ui/Button"
import { knowledgeApi } from "@/lib/api"
import { getAccessToken } from "@/lib/auth"

export default function KnowledgeUploadPage({ params }: { params: Promise<{ id: string; workspaceId: string }> }) {
  const resolvedParams = use(params)
  const router = useRouter()
  const fileInputRef = useRef<HTMLInputElement>(null)
  
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setSelectedFile(e.target.files[0])
      setError(null)
      setSuccess(false)
    }
  }

  const handleUpload = async () => {
    const token = getAccessToken()
    if (!selectedFile || !token) return
    setIsUploading(true)
    setError(null)

    try {
      await knowledgeApi.upload(token, resolvedParams.workspaceId, selectedFile)
      setSuccess(true)
      setSelectedFile(null)
      setTimeout(() => {
        router.push(`/organizations/${resolvedParams.id}/workspaces/${resolvedParams.workspaceId}/knowledge/sources`)
      }, 1500)
    } catch (err: any) {
      setError(err.detail || "Failed to upload file")
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <GlassPanel className="p-8">
        <h2 className="text-lg font-bold mb-6">Upload Knowledge Source</h2>

        {/* Upload Zone */}
        <div 
          className="border-2 border-dashed border-[var(--color-border-subtle)] rounded-[var(--radius-lg)] p-12 text-center hover:border-[var(--color-primary-base)] hover:bg-[rgba(124,58,237,0.05)] transition-colors cursor-pointer group"
          onClick={() => fileInputRef.current?.click()}
        >
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleFileSelect} 
            className="hidden" 
          />
          <div className="w-12 h-12 rounded-full bg-[rgba(255,255,255,0.05)] flex items-center justify-center mx-auto mb-4 group-hover:bg-[rgba(124,58,237,0.1)] transition-colors">
            <UploadCloud className="w-6 h-6 text-[var(--color-text-secondary)] group-hover:text-[var(--color-primary-light)] transition-colors" />
          </div>
          <p className="text-sm font-medium mb-1">Click to browse or drag & drop</p>
          <p className="text-xs text-[var(--color-text-muted)]">
            PDF, Markdown, TXT, CSV, Code files (max 50MB)
          </p>
        </div>

        {/* Selected File */}
        {selectedFile && (
          <div className="mt-6 p-4 rounded-[var(--radius-md)] bg-[rgba(0,0,0,0.2)] border border-[var(--color-border-subtle)] flex items-center justify-between">
            <div className="flex items-center gap-3">
              <File className="w-5 h-5 text-[var(--color-primary-light)]" />
              <div>
                <p className="text-sm font-medium">{selectedFile.name}</p>
                <p className="text-xs text-[var(--color-text-muted)]">{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
              </div>
            </div>
            <div className="flex gap-2">
              <Button variant="ghost" size="sm" onClick={() => setSelectedFile(null)} disabled={isUploading}>
                Cancel
              </Button>
              <Button variant="primary" size="sm" onClick={handleUpload} disabled={isUploading}>
                {isUploading ? <span className="spinner-ring" /> : "Upload to Atlas"}
              </Button>
            </div>
          </div>
        )}

        {/* Feedback */}
        {error && (
          <div className="mt-4 p-3 bg-[rgba(239,68,68,0.1)] border border-[rgba(239,68,68,0.3)] rounded-[var(--radius-sm)] flex items-center gap-2 text-[var(--color-accent-red)] text-sm">
            <AlertCircle className="w-4 h-4" /> {error}
          </div>
        )}
        {success && (
          <div className="mt-4 p-3 bg-[rgba(34,197,94,0.1)] border border-[rgba(34,197,94,0.3)] rounded-[var(--radius-sm)] flex items-center gap-2 text-[var(--color-accent-green)] text-sm">
            <CheckCircle2 className="w-4 h-4" /> Upload successful! Indexing started.
          </div>
        )}
      </GlassPanel>
    </div>
  )
}
