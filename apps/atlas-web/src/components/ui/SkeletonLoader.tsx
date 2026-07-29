import React from "react"
import { cn } from "@/lib/utils"

export function SkeletonLoader({ className, lines = 1 }: { className?: string; lines?: number }) {
  return (
    <div className={cn("animate-pulse w-full", className)}>
      {Array.from({ length: lines }).map((_, i) => (
        <div 
          key={i} 
          className={cn(
            "h-4 bg-[rgba(255,255,255,0.05)] rounded mb-3", 
            i === lines - 1 && lines > 1 ? "w-2/3" : "w-full"
          )} 
        />
      ))}
    </div>
  )
}
