import React from "react"
import { cn } from "@/lib/utils"

export interface GlassPanelProps extends React.HTMLAttributes<HTMLDivElement> {
  glow?: boolean
}

export const GlassPanel = React.forwardRef<HTMLDivElement, GlassPanelProps>(
  ({ className, glow = false, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "bg-[rgba(17,24,39,0.6)] backdrop-blur-md border border-[var(--color-border-subtle)] rounded-[var(--radius-xl)]",
          glow && "hover:border-[rgba(124,58,237,0.4)] hover:shadow-[var(--shadow-glow)] transition-all duration-300",
          className
        )}
        {...props}
      >
        {children}
      </div>
    )
  }
)
GlassPanel.displayName = "GlassPanel"
