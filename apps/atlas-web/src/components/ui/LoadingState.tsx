import React from "react"
import { Loader2 } from "lucide-react"
import { cn } from "@/lib/utils"

interface LoadingStateProps {
  message?: string
  className?: string
}

export function LoadingState({ message = "Loading...", className }: LoadingStateProps) {
  return (
    <div className={cn("flex flex-col items-center justify-center p-12 min-h-[200px]", className)}>
      <Loader2 className="w-8 h-8 animate-spin text-[var(--color-primary-base)] mb-4" />
      <p className="text-[var(--color-text-secondary)] text-sm animate-pulse">{message}</p>
    </div>
  )
}
