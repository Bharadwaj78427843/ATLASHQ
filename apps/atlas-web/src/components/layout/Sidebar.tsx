"use client"

import React from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { useActiveOrganization } from "@/contexts/OrganizationContext"
import { useWorkspaces } from "@/features/workspaces/hooks/useWorkspaces"
import {
  Home, Folder, GitBranch, Box, Rocket,
  Bot, BookOpen, Search,
  Users, Settings as SettingsIcon,
  ChevronDown
} from "lucide-react"

export function Sidebar() {
  const pathname = usePathname()
  const { activeOrganization, setActiveOrganizationId } = useActiveOrganization()
  const orgId = activeOrganization?.id || ""
  const { data: workspacesData } = useWorkspaces(orgId)

  // Use first workspace as the "active" workspace for navigation
  const activeWorkspace = workspacesData?.items?.[0]
  const wsId = activeWorkspace?.id || ""

  const base = orgId && wsId ? `/organizations/${orgId}/workspaces/${wsId}` : null

  const SECTIONS = [
    {
      title: "WORKSPACE",
      items: [
        { name: "Ask Atlas", icon: Home, href: "/dashboard" },
        { name: "Projects", icon: Folder, href: base ? `${base}/projects` : "/projects" },
        { name: "Workspaces", icon: Box, href: orgId ? `/organizations/${orgId}` : "/workspaces" },
      ]
    },
    {
      title: "KNOWLEDGE",
      items: [
        { name: "Knowledge", icon: BookOpen, href: base ? `${base}/knowledge` : "/knowledge" },
        { name: "Repositories", icon: GitBranch, href: base ? `${base}/knowledge/repositories` : "/repositories" },
        { name: "Search", icon: Search, href: base ? `${base}/knowledge` : "/search" },
      ]
    },
    {
      title: "AI & AUTOMATION",
      items: [
        { name: "Agents", icon: Bot, href: "/agents" },
        { name: "Deployments", icon: Rocket, href: "/deployments" },
      ]
    },
    {
      title: "SETTINGS",
      items: [
        { name: "Organizations", icon: Users, href: "/organizations" },
        { name: "AI Settings", icon: SettingsIcon, href: "/settings/ai" },
      ]
    }
  ]

  const isActive = (href: string) => {
    if (href === "/dashboard") return pathname === href
    return pathname.startsWith(href)
  }

  return (
    <aside className="w-64 flex flex-col h-screen border-r border-[var(--color-border-subtle)] bg-[var(--color-background)]">
      {/* Brand */}
      <div className="h-16 flex items-center px-6 border-b border-[var(--color-border-subtle)] gap-3 shrink-0">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[var(--color-primary-base)] to-[var(--color-primary-light)] flex items-center justify-center shadow-[var(--shadow-glow)]">
          <span className="text-white font-bold text-lg leading-none">⬡</span>
        </div>
        <span className="font-semibold text-lg tracking-tight">AtlasHQ</span>
      </div>

      {/* Organization Switcher */}
      {activeOrganization && (
        <div className="px-4 py-3 border-b border-[var(--color-border-subtle)]">
          <div className="flex items-center gap-2 px-3 py-2 rounded-[var(--radius-md)] bg-[rgba(255,255,255,0.04)] border border-[var(--color-border-subtle)] cursor-pointer hover:bg-[rgba(255,255,255,0.07)] transition-colors">
            <div className="w-6 h-6 rounded bg-[var(--color-primary-base)] flex items-center justify-center text-xs font-bold text-white shrink-0">
              {activeOrganization.name.charAt(0).toUpperCase()}
            </div>
            <span className="text-sm font-medium text-[var(--color-text-primary)] truncate flex-1">{activeOrganization.name}</span>
            {activeWorkspace && (
              <span className="text-[10px] text-[var(--color-text-muted)] truncate max-w-[60px]">{activeWorkspace.name}</span>
            )}
          </div>
        </div>
      )}

      <div className="p-4">
        <Link
          href="/dashboard"
          className="w-full flex items-center justify-center gap-2 bg-[rgba(124,58,237,0.15)] text-[var(--color-primary-light)] border border-[rgba(124,58,237,0.3)] rounded-[var(--radius-md)] py-2 text-sm font-medium hover:bg-[rgba(124,58,237,0.2)] transition-colors"
        >
          <span className="text-lg leading-none">✦</span> Ask Atlas
        </Link>
      </div>

      <div className="flex-1 overflow-y-auto px-3 pb-6 space-y-6">
        {SECTIONS.map((section) => (
          <div key={section.title}>
            <h3 className="px-3 text-xs font-semibold text-[var(--color-text-muted)] mb-2 tracking-wider">
              {section.title}
            </h3>
            <ul className="space-y-0.5">
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
              {activeOrganization?.name || "No Organization"}
            </span>
          </div>
          <p className="text-xs text-[var(--color-text-secondary)] mb-2">
            {activeWorkspace?.name || "No workspace"}
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
