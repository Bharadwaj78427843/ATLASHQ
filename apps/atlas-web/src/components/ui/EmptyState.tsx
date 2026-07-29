import React from "react"
import { LucideIcon } from "lucide-react"
import { GlassPanel } from "./GlassPanel"
import { Button } from "./Button"

interface EmptyStateProps {
  icon: LucideIcon
  title: string
  description: string
  actionLabel?: string
  onAction?: () => void
}

export function EmptyState({ icon: Icon, title, description, actionLabel, onAction }: EmptyStateProps) {
  return (
    <GlassPanel className="flex flex-col items-center justify-center p-12 text-center">
      <div className="w-16 h-16 rounded-full bg-[rgba(255,255,255,0.03)] flex items-center justify-center mb-6 border border-[rgba(255,255,255,0.05)]">
        <Icon className="w-8 h-8 text-[var(--color-text-muted)]" />
      </div>
      <h3 className="text-xl font-medium mb-2 text-[var(--color-text-primary)]">{title}</h3>
      <p className="text-[var(--color-text-secondary)] mb-8 max-w-md mx-auto">
        {description}
      </p>
      {actionLabel && onAction && (
        <Button variant="primary" onClick={onAction}>
          {actionLabel}
        </Button>
      )}
    </GlassPanel>
  )
}
