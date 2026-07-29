import React from "react"
import { cn } from "@/lib/utils"

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  icon?: React.ReactNode
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, icon, ...props }, ref) => {
    return (
      <div className="relative flex items-center w-full">
        {icon && (
          <div className="absolute left-3 flex items-center justify-center text-[var(--color-text-muted)]">
            {icon}
          </div>
        )}
        <input
          ref={ref}
          className={cn(
            "flex h-10 w-full rounded-[var(--radius-sm)] border border-[var(--color-border-subtle)] bg-[var(--color-panel)] px-3 py-2 text-sm placeholder:text-[var(--color-text-muted)] focus:outline-none focus:ring-1 focus:ring-[var(--color-primary-base)] focus:border-[var(--color-primary-base)] disabled:cursor-not-allowed disabled:opacity-50 transition-colors",
            icon && "pl-10",
            className
          )}
          {...props}
        />
      </div>
    )
  }
)
Input.displayName = "Input"
