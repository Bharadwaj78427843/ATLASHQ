import React from "react"
import { cn } from "@/lib/utils"

interface FormFieldProps {
  label: string
  htmlFor?: string
  description?: string
  error?: string
  required?: boolean
  children: React.ReactNode
  className?: string
}

export function FormField({
  label,
  htmlFor,
  description,
  error,
  required,
  children,
  className,
}: FormFieldProps) {
  return (
    <div className={cn("space-y-2", className)}>
      <div className="flex justify-between items-baseline">
        <label
          htmlFor={htmlFor}
          className="text-sm font-medium text-[var(--color-text-secondary)]"
        >
          {label}
          {required && <span className="text-[var(--color-primary-base)] ml-1">*</span>}
        </label>
        {error && <span className="text-xs text-[var(--color-accent-red)]">{error}</span>}
      </div>
      
      {children}
      
      {description && !error && (
        <p className="text-xs text-[var(--color-text-muted)] mt-1.5">{description}</p>
      )}
    </div>
  )
}
