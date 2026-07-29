import React from "react"
import { cn } from "@/lib/utils"

export type StatusType = "success" | "error" | "warning" | "info" | "neutral"

interface StatusBadgeProps {
  status: StatusType
  label: string
  className?: string
}

export function StatusBadge({ status, label, className }: StatusBadgeProps) {
  const styles = {
    success: "bg-[rgba(34,197,94,0.1)] text-[var(--color-accent-green)] border-[rgba(34,197,94,0.3)]",
    error: "bg-[rgba(239,68,68,0.1)] text-[var(--color-accent-red)] border-[rgba(239,68,68,0.3)]",
    warning: "bg-[rgba(245,158,11,0.1)] text-[var(--color-accent-yellow)] border-[rgba(245,158,11,0.3)]",
    info: "bg-[rgba(59,130,246,0.1)] text-[var(--color-accent-blue)] border-[rgba(59,130,246,0.3)]",
    neutral: "bg-[rgba(255,255,255,0.05)] text-[var(--color-text-secondary)] border-[rgba(255,255,255,0.1)]",
  }

  return (
    <span className={cn("inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full border text-xs font-medium", styles[status], className)}>
      <span className={cn("w-1.5 h-1.5 rounded-full", {
        "bg-[var(--color-accent-green)]": status === "success",
        "bg-[var(--color-accent-red)]": status === "error",
        "bg-[var(--color-accent-yellow)]": status === "warning",
        "bg-[var(--color-accent-blue)]": status === "info",
        "bg-[var(--color-text-muted)]": status === "neutral",
      })} />
      {label}
    </span>
  )
}
