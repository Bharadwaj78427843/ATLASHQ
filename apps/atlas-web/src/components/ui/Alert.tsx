import React from "react"
import { AlertCircle, CheckCircle2, Info, AlertTriangle } from "lucide-react"
import { cn } from "@/lib/utils"

export type AlertVariant = "error" | "success" | "info" | "warning"

interface AlertProps {
  variant?: AlertVariant
  title?: string
  children: React.ReactNode
  className?: string
}

export function Alert({ variant = "info", title, children, className }: AlertProps) {
  const styles = {
    error: "bg-[rgba(239,68,68,0.1)] border-[rgba(239,68,68,0.3)] text-[var(--color-accent-red)]",
    success: "bg-[rgba(34,197,94,0.1)] border-[rgba(34,197,94,0.3)] text-[var(--color-accent-green)]",
    warning: "bg-[rgba(245,158,11,0.1)] border-[rgba(245,158,11,0.3)] text-[var(--color-accent-yellow)]",
    info: "bg-[rgba(59,130,246,0.1)] border-[rgba(59,130,246,0.3)] text-[var(--color-accent-blue)]",
  }

  const icons = {
    error: AlertCircle,
    success: CheckCircle2,
    warning: AlertTriangle,
    info: Info,
  }

  const Icon = icons[variant]

  return (
    <div className={cn("p-4 border rounded-[var(--radius-md)] flex items-start gap-3", styles[variant], className)} role="alert">
      <Icon className="w-5 h-5 shrink-0 mt-0.5" />
      <div className="flex-1">
        {title && <h5 className="font-medium mb-1">{title}</h5>}
        <div className="text-sm opacity-90">{children}</div>
      </div>
    </div>
  )
}
