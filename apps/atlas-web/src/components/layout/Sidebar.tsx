"use client"

import React, { useEffect, useMemo, useState } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { useWorkspaceSelection } from "@/hooks/useWorkspaceSelection"
import {
  Home,
  Folder,
  GitBranch,
  Box,
  Rocket,
  Bot,
  FileText,
  Search,
  Users,
  Settings as SettingsIcon,
  ChevronDown,
  ChevronRight
} from "lucide-react"

type NavItem = {
  name: string
  icon: React.ComponentType<{ className?: string }>
  href: string
}

type NavSection = {
  key: string
  title: string
  items: NavItem[]
}

const EXPANDED_STORAGE_KEY = "atlas_sidebar_expanded_sections"

export function Sidebar() {
  const pathname = usePathname()
  const { activeOrganization, activeWorkspace, setWorkspaceId, workspaces } = useWorkspaceSelection()
  const orgId = activeOrganization?.id ?? ""
  const wsId = activeWorkspace?.id ?? ""
  const base = orgId && wsId ? `/organizations/${orgId}/workspaces/${wsId}` : null

  const sections: NavSection[] = useMemo(
    () => [
      {
        key: "workspace",
        title: "Workspace",
        items: [
          { name: "Projects", icon: Folder, href: base ? `${base}/projects` : "/projects" },
          { name: "Workspaces", icon: Box, href: orgId ? `/organizations/${orgId}` : "/workspaces" },
        ],
      },
      {
        key: "knowledge",
        title: "Knowledge",
        items: [
          { name: "Documents", icon: FileText, href: base ? `${base}/knowledge/sources` : "/knowledge" },
          { name: "Repositories", icon: GitBranch, href: base ? `${base}/knowledge/repositories` : "/repositories" },
          { name: "Search", icon: Search, href: base ? `${base}/knowledge` : "/search" },
        ],
      },
      {
        key: "ai",
        title: "AI",
        items: [
          { name: "Atlas Chat", icon: Home, href: "/dashboard" },
          { name: "Agents", icon: Bot, href: "/agents" },
          { name: "Deployments", icon: Rocket, href: "/deployments" },
        ],
      },
      {
        key: "administration",
        title: "Administration",
        items: [
          { name: "Organizations", icon: Users, href: "/organizations" },
          { name: "AI Settings", icon: SettingsIcon, href: "/settings/ai" },
        ],
      },
    ],
    [base, orgId]
  )

  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    workspace: true,
    knowledge: true,
    ai: true,
    administration: true,
  })

  useEffect(() => {
    const raw = localStorage.getItem(EXPANDED_STORAGE_KEY)
    if (!raw) {
      return
    }

    try {
      const parsed = JSON.parse(raw) as Record<string, boolean>
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setExpandedSections((prev) => ({ ...prev, ...parsed }))
    } catch {
      // ignore invalid local storage payload
    }
  }, [])

  const toggleSection = (key: string) => {
    setExpandedSections((prev) => {
      const next = { ...prev, [key]: !prev[key] }
      localStorage.setItem(EXPANDED_STORAGE_KEY, JSON.stringify(next))
      return next
    })
  }

  const isActive = (href: string) => {
    if (href === "/dashboard") return pathname === href
    return pathname.startsWith(href)
  }

  const activeWorkspaceName = activeWorkspace?.name || workspaces[0]?.name || "Select workspace"
  const activeOrgName = activeOrganization?.name || "Select organization"

  return (
    <aside className="w-64 flex flex-col h-screen border-r border-[var(--color-border-subtle)] bg-[var(--color-background)]">
      {/* Brand */}
      <div className="h-16 flex items-center px-6 border-b border-[var(--color-border-subtle)] gap-3 shrink-0">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[var(--color-primary-base)] to-[var(--color-primary-light)] flex items-center justify-center shadow-[var(--shadow-glow)]">
          <span className="text-white font-bold text-lg leading-none">⬡</span>
        </div>
        <span className="font-semibold text-lg tracking-tight">AtlasHQ</span>
      </div>

      {/* Organization + workspace context */}
      {activeOrganization && (
        <div className="px-4 py-3 border-b border-[var(--color-border-subtle)] space-y-2">
          <div className="flex items-center gap-2 px-3 py-2 rounded-[var(--radius-md)] bg-[rgba(255,255,255,0.04)] border border-[var(--color-border-subtle)]">
            <div className="w-6 h-6 rounded bg-[var(--color-primary-base)] flex items-center justify-center text-xs font-bold text-white shrink-0">
              {activeOrganization.name.charAt(0).toUpperCase()}
            </div>
            <span className="text-sm font-medium text-[var(--color-text-primary)] truncate flex-1">{activeOrganization.name}</span>
          </div>
          {workspaces.length > 0 ? (
            <select
              className="w-full px-2.5 py-2 rounded-[var(--radius-md)] bg-[var(--color-panel)] border border-[var(--color-border-subtle)] text-xs text-[var(--color-text-secondary)]"
              value={wsId}
              onChange={(event) => setWorkspaceId(event.target.value)}
            >
              {workspaces.map((workspace) => (
                <option key={workspace.id} value={workspace.id}>
                  {workspace.name}
                </option>
              ))}
            </select>
          ) : null}
        </div>
      )}

      <div className="p-4">
        <Link
          href="/dashboard"
          className="w-full flex items-center justify-center gap-2 bg-[rgba(124,58,237,0.15)] text-[var(--color-primary-light)] border border-[rgba(124,58,237,0.3)] rounded-[var(--radius-md)] py-2 text-sm font-medium hover:bg-[rgba(124,58,237,0.2)] transition-colors"
        >
          <span className="text-lg leading-none">✦</span> Dashboard
        </Link>
      </div>

      <div className="flex-1 overflow-y-auto px-3 pb-6 space-y-6">
        {sections.map((section) => (
          <div key={section.key}>
            <button
              type="button"
              onClick={() => toggleSection(section.key)}
              className="w-full px-3 text-xs font-semibold text-[var(--color-text-muted)] mb-2 tracking-wider flex items-center justify-between hover:text-[var(--color-text-secondary)]"
            >
              {section.title}
              {expandedSections[section.key] ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
            </button>
            <ul className={cn("space-y-0.5", !expandedSections[section.key] && "hidden")}>
              {section.items.map((item) => {
                const active = isActive(item.href)
                return (
                  <li key={item.name}>
                    <Link
                      href={item.href}
                      className={cn(
                        "flex items-center gap-3 px-3 py-1.5 rounded-[var(--radius-sm)] text-sm font-medium transition-colors",
                        active
                          ? "bg-[rgba(255,255,255,0.08)] text-[var(--color-text-primary)]"
                          : "text-[var(--color-text-secondary)] hover:bg-[rgba(255,255,255,0.04)] hover:text-[var(--color-text-primary)]"
                      )}
                    >
                      <item.icon className="w-4 h-4" />
                      {item.name}
                    </Link>
                  </li>
                )
              })}
            </ul>
          </div>
        ))}
      </div>

      {/* Bottom status */}
      <div className="p-4 border-t border-[var(--color-border-subtle)] shrink-0">
        <div className="bg-[var(--color-panel)] rounded-[var(--radius-md)] p-3 border border-[var(--color-border-subtle)]">
          <div className="flex justify-between items-center mb-1">
            <span className="text-sm font-medium text-[var(--color-primary-light)]">
              {activeOrgName}
            </span>
          </div>
          <p className="text-xs text-[var(--color-text-secondary)] mb-2">
            {activeWorkspaceName}
          </p>
          <Link
            href="/organizations"
            className="block w-full text-xs py-1.5 border border-[var(--color-border-subtle)] rounded-[var(--radius-sm)] text-center text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] hover:bg-[rgba(255,255,255,0.05)] transition-colors"
          >
            Switch Organization
          </Link>
        </div>
      </div>
    </aside>
  )
}
