"use client"

import React, { useState } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { Search, Command } from "lucide-react"
import { useAuth } from "@/contexts/AuthContext"
import { useWorkspaceSelection } from "@/hooks/useWorkspaceSelection"
import { Button } from "@/components/ui/Button"

export function TopBar() {
  const { user } = useAuth()
  const router = useRouter()
  const { activeOrganization, activeWorkspace, workspaces, setWorkspaceId } = useWorkspaceSelection()
  const [query, setQuery] = useState("")

  const initials = user
    ? ([user.first_name, user.last_name].filter(Boolean).map((n) => n![0].toUpperCase()).join("") || user.username[0].toUpperCase())
    : "?"

  const displayName = user
    ? ([user.first_name, user.last_name].filter(Boolean).join(" ") || user.username)
    : "Guest"

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return
    const ws = activeWorkspace
    const org = activeOrganization
    if (org && ws) {
      router.push(`/organizations/${org.id}/workspaces/${ws.id}/knowledge?q=${encodeURIComponent(query)}`)
    }
    setQuery("")
  }

  return (
    <header className="h-16 flex items-center justify-between px-6 border-b border-[var(--color-border-subtle)] bg-[var(--color-background)] shrink-0">

      {/* Workspace Switcher */}
      <div className="flex items-center gap-2">
        {activeOrganization ? (
          <div className="flex items-center gap-2 bg-[var(--color-panel)] border border-[var(--color-border-subtle)] px-3 py-1.5 rounded-[var(--radius-md)]">
            <div className="w-5 h-5 rounded bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-[10px] font-bold text-white">
              {activeOrganization.name?.[0]?.toUpperCase() || "A"}
            </div>
            <Link href={`/organizations/${activeOrganization.id}`} className="text-xs text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]">
              {activeOrganization.name}
            </Link>
            {workspaces.length > 0 ? (
              <select
                value={activeWorkspace?.id || ""}
                onChange={(e) => setWorkspaceId(e.target.value)}
                className="bg-transparent text-sm font-medium focus:outline-none"
              >
                {workspaces.map((workspace) => (
                  <option key={workspace.id} value={workspace.id}>
                    {workspace.name}
                  </option>
                ))}
              </select>
            ) : (
              <span className="text-sm font-medium">Select Workspace</span>
            )}
          </div>
        ) : (
          <Link
            href="/organizations"
            className="flex items-center gap-2 bg-[var(--color-panel)] border border-[var(--color-border-subtle)] px-3 py-1.5 rounded-[var(--radius-md)] cursor-pointer hover:border-[rgba(255,255,255,0.2)] transition-colors"
          >
            <span className="text-sm font-medium">Select Workspace</span>
          </Link>
        )}
      </div>

      {/* Global Search */}
      <form onSubmit={handleSearch} className="flex-1 max-w-xl mx-8">
        <div className="relative">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-text-muted)]" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search knowledge or ask Atlas anything..."
            className="w-full bg-[var(--color-panel)] border border-[var(--color-border-subtle)] rounded-full py-2 pl-10 pr-12 text-sm text-[var(--color-text-primary)] focus:outline-none focus:border-[rgba(124,58,237,0.5)] focus:ring-1 focus:ring-[rgba(124,58,237,0.5)] transition-all"
          />
          <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-1 text-[10px] text-[var(--color-text-muted)] font-mono font-medium border border-[var(--color-border-subtle)] rounded px-1.5 py-0.5 bg-[var(--color-background)]">
            <Command className="w-3 h-3" /> K
          </div>
        </div>
      </form>

      {/* Right Actions */}
      <div className="flex items-center gap-4">
        <Link href="/dashboard">
          <Button variant="primary" size="sm" className="rounded-full gap-1.5 px-4 font-semibold">
            <span>✦</span> Atlas Chat
          </Button>
        </Link>

        <div className="w-px h-6 bg-[var(--color-border-subtle)] mx-1" />

        <div className="flex items-center gap-3 cursor-pointer">
          <div className="text-right hidden sm:block">
            <div className="text-sm font-medium leading-tight">{displayName}</div>
            <div className="text-[10px] text-[var(--color-text-muted)]">
              {activeOrganization?.name || "No Organization"}
            </div>
          </div>
          <div className="w-8 h-8 rounded-full bg-[var(--color-panel)] border border-[var(--color-border-subtle)] flex items-center justify-center text-xs font-semibold overflow-hidden">
            {initials}
          </div>
        </div>
      </div>
    </header>
  )
}
