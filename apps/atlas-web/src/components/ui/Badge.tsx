import React from "react"
import { cn } from "@/lib/utils"

export type BadgeVariant = "default" | "success" | "warning" | "error" | "info" | "outline"

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant
}

export function Badge({ variant = "default", className, ...props }: BadgeProps) {
  const variants = {
    default: "bg-[var(--color-panel)] text-[var(--color-text-primary)] border-[var(--color-border-subtle)]",
    success: "bg-[rgba(34,197,94,0.1)] text-[var(--color-accent-green)] border-[rgba(34,197,94,0.2)]",
    warning: "bg-[rgba(245,158,11,0.1)] text-[var(--color-accent-yellow)] border-[rgba(245,158,11,0.2)]",
    error: "bg-[rgba(239,68,68,0.1)] text-[var(--color-accent-red)] border-[rgba(239,68,68,0.2)]",
    info: "bg-[rgba(59,130,246,0.1)] text-[var(--color-accent-blue)] border-[rgba(59,130,246,0.2)]",
    outline: "bg-transparent text-[var(--color-text-secondary)] border-[var(--color-border-subtle)]",
  }

  return (
    <span
      className={cn(
        "inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border",
        variants[variant],
        className
      )}
      {...props}
    />
  )
}
