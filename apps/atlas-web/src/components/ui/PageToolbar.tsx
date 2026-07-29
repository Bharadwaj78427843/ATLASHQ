import React from "react"
import { cn } from "@/lib/utils"

export function PageToolbar({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={cn("flex flex-wrap items-center gap-3 mb-6", className)}>
      {children}
    </div>
  )
}
