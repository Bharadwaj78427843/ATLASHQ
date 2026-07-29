import React from "react"
import { AlertTriangle } from "lucide-react"
import { GlassPanel } from "./GlassPanel"
import { Button } from "./Button"

interface ErrorStateProps {
  title?: string
  error: Error | string
  onRetry?: () => void
}

export function ErrorState({ title = "Something went wrong", error, onRetry }: ErrorStateProps) {
  const message = typeof error === "string" ? error : error.message
  return (
    <GlassPanel className="flex flex-col items-center justify-center p-12 text-center border-[rgba(239,68,68,0.3)]">
      <div className="w-16 h-16 rounded-full bg-[rgba(239,68,68,0.1)] flex items-center justify-center mb-6 border border-[rgba(239,68,68,0.2)]">
        <AlertTriangle className="w-8 h-8 text-[var(--color-accent-red)]" />
      </div>
      <h3 className="text-xl font-medium mb-2 text-[var(--color-text-primary)]">{title}</h3>
      <p className="text-[var(--color-text-secondary)] mb-8 max-w-md mx-auto">
        {message}
      </p>
      {onRetry && (
        <Button variant="primary" onClick={onRetry}>
          Retry
        </Button>
      )}
    </GlassPanel>
  )
}
