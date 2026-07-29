import React from "react"
import { cn } from "@/lib/utils"
import { GlassPanel } from "./GlassPanel"

export interface MetricCardProps {
  title: string
  value: string | number
  trend?: string
  trendDirection?: "up" | "down" | "neutral"
  icon?: React.ReactNode
  className?: string
}

export const MetricCard = React.memo(function MetricCard({ title, value, trend, trendDirection = "neutral", icon, className }: MetricCardProps) {
  const trendColor = {
    up: "text-[var(--color-accent-green)]",
    down: "text-[var(--color-accent-red)]",
    neutral: "text-[var(--color-text-muted)]"
  }[trendDirection]

  return (
    <GlassPanel className={cn("p-5 flex flex-col justify-between gap-4", className)} glow>
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-[var(--color-text-secondary)]">{title}</h3>
        {icon && <div className="text-[var(--color-primary-base)] bg-[rgba(124,58,237,0.1)] p-2 rounded-lg">{icon}</div>}
      </div>
      <div>
        <div className="text-3xl font-bold text-[var(--color-text-primary)] tracking-tight">{value}</div>
        {trend && (
          <div className={cn("text-xs mt-1 font-medium flex items-center gap-1", trendColor)}>
            {trendDirection === "up" && "↑"}
            {trendDirection === "down" && "↓"}
            {trend}
          </div>
        )}
      </div>
    </GlassPanel>
  )
})
