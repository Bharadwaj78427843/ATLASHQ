"use client"

import React from "react"
import { Sparkles, Plus, Clock, FileText, Database, Shield, Zap, Box, PlayCircle } from "lucide-react"

export function RightPanel() {
  return (
    <aside className="w-80 border-l border-[var(--color-border-subtle)] bg-[var(--color-background)] h-[calc(100vh-64px)] flex flex-col shrink-0 overflow-y-auto">
      {/* AI Assistant Section */}
      <div className="p-5 border-b border-[var(--color-border-subtle)]">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold flex items-center gap-2">
            <span className="text-[var(--color-primary-base)]">✦</span> AI Assistant
          </h3>
          <button className="text-xs text-[var(--color-text-secondary)] flex items-center gap-1 hover:text-[var(--color-text-primary)] transition-colors">
            <Plus className="w-3 h-3" /> New Chat
          </button>
        </div>
        
        <div className="space-y-3">
          <div className="flex items-start justify-between group cursor-pointer">
            <div className="flex gap-2">
              <Clock className="w-4 h-4 text-[var(--color-text-muted)] mt-0.5 group-hover:text-[var(--color-primary-light)] transition-colors" />
              <p className="text-xs text-[var(--color-text-secondary)] group-hover:text-[var(--color-text-primary)] transition-colors line-clamp-2 leading-relaxed">
                Analyze authentication flow
              </p>
            </div>
            <span className="text-[10px] text-[var(--color-text-muted)] shrink-0">2m ago</span>
          </div>
          
          <div className="flex items-start justify-between group cursor-pointer">
            <div className="flex gap-2">
              <Clock className="w-4 h-4 text-[var(--color-text-muted)] mt-0.5 group-hover:text-[var(--color-primary-light)] transition-colors" />
              <p className="text-xs text-[var(--color-text-secondary)] group-hover:text-[var(--color-text-primary)] transition-colors line-clamp-2 leading-relaxed">
                Why is this API slow?
              </p>
            </div>
            <span className="text-[10px] text-[var(--color-text-muted)] shrink-0">15m ago</span>
          </div>

          <div className="flex items-start justify-between group cursor-pointer">
            <div className="flex gap-2">
              <Clock className="w-4 h-4 text-[var(--color-text-muted)] mt-0.5 group-hover:text-[var(--color-primary-light)] transition-colors" />
              <p className="text-xs text-[var(--color-text-secondary)] group-hover:text-[var(--color-text-primary)] transition-colors line-clamp-2 leading-relaxed">
                Generate unit tests
              </p>
            </div>
            <span className="text-[10px] text-[var(--color-text-muted)] shrink-0">1h ago</span>
          </div>
        </div>

        <button className="text-xs text-[var(--color-primary-light)] mt-4 hover:underline">
          View all conversations →
        </button>
      </div>

      {/* Recent Uploads Section */}
      <div className="p-5 border-b border-[var(--color-border-subtle)]">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold flex items-center gap-2">
            <Database className="w-4 h-4 text-[var(--color-accent-blue)]" /> Recent Uploads
          </h3>
          <button className="text-xs text-[var(--color-primary-light)] hover:underline">
            View all
          </button>
        </div>

        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded bg-[rgba(59,130,246,0.1)] text-[var(--color-accent-blue)] flex items-center justify-center">
                <FileText className="w-4 h-4" />
              </div>
              <div>
                <p className="text-xs font-medium text-[var(--color-text-primary)]">database-schema.sql</p>
                <p className="text-[10px] text-[var(--color-text-muted)]">2m ago</p>
              </div>
            </div>
            <span className="text-xs text-[var(--color-text-muted)]">12 KB</span>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded bg-[rgba(239,68,68,0.1)] text-[var(--color-accent-red)] flex items-center justify-center">
                <FileText className="w-4 h-4" />
              </div>
              <div>
                <p className="text-xs font-medium text-[var(--color-text-primary)]">api-docs.pdf</p>
                <p className="text-[10px] text-[var(--color-text-muted)]">15m ago</p>
              </div>
            </div>
            <span className="text-xs text-[var(--color-text-muted)]">1.2 MB</span>
          </div>
        </div>

        <div className="mt-5 border border-dashed border-[var(--color-border-subtle)] rounded-[var(--radius-md)] p-4 text-center cursor-pointer hover:bg-[rgba(255,255,255,0.02)] transition-colors">
          <p className="text-xs text-[var(--color-text-secondary)] font-medium">
            ↑ Drop files here or click to upload
          </p>
        </div>
      </div>

      {/* Running Agents Section */}
      <div className="p-5">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold flex items-center gap-2">
            <Zap className="w-4 h-4 text-[var(--color-accent-orange)]" /> Running Agents
          </h3>
          <button className="text-xs text-[var(--color-primary-light)] hover:underline">
            View all
          </button>
        </div>

        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-[rgba(124,58,237,0.1)] text-[var(--color-primary-light)] flex items-center justify-center border border-[rgba(124,58,237,0.2)]">
                <PlayCircle className="w-4 h-4" />
              </div>
              <div>
                <p className="text-xs font-medium text-[var(--color-text-primary)]">Code Reviewer</p>
                <p className="text-[10px] text-[var(--color-text-secondary)]">Reviewing PR #128</p>
              </div>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="text-[10px] text-[var(--color-text-muted)]">2m ago</span>
              <div className="w-1.5 h-1.5 rounded-full bg-[var(--color-primary-base)] animate-pulse" />
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-[rgba(34,197,94,0.1)] text-[var(--color-accent-green)] flex items-center justify-center border border-[rgba(34,197,94,0.2)]">
                <Shield className="w-4 h-4" />
              </div>
              <div>
                <p className="text-xs font-medium text-[var(--color-text-primary)]">Bug Finder</p>
                <p className="text-[10px] text-[var(--color-text-secondary)]">Scanning codebase</p>
              </div>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="text-[10px] text-[var(--color-text-muted)]">15m ago</span>
              <div className="w-1.5 h-1.5 rounded-full bg-[var(--color-accent-green)] animate-pulse" />
            </div>
          </div>
        </div>
      </div>
    </aside>
  )
}
