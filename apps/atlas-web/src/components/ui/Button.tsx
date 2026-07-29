import React from "react"
import { cn } from "@/lib/utils"

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost" | "danger"
  size?: "sm" | "md" | "lg" | "icon"
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", size = "md", ...props }, ref) => {
    const variants = {
      primary: "bg-[var(--color-primary-base)] text-white hover:bg-[var(--color-primary-hover)] border-transparent shadow-[var(--shadow-glow)]",
      secondary: "bg-[var(--color-panel)] text-[var(--color-text-primary)] hover:bg-[var(--color-card)] border-[var(--color-border-subtle)]",
      ghost: "bg-transparent text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] hover:bg-[rgba(255,255,255,0.05)] border-transparent",
      danger: "bg-[var(--color-accent-red)] text-white hover:opacity-90 border-transparent",
    }
    
    const sizes = {
      sm: "h-8 px-3 text-xs",
      md: "h-10 px-4 py-2 text-sm",
      lg: "h-12 px-8 text-base",
      icon: "h-10 w-10 p-2 flex items-center justify-center",
    }

    return (
      <button
        ref={ref}
        className={cn(
          "inline-flex items-center justify-center rounded-[var(--radius-sm)] border font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-[var(--color-primary-base)] focus:ring-offset-2 focus:ring-offset-[var(--color-background)] disabled:opacity-50 disabled:cursor-not-allowed",
          variants[variant],
          sizes[size],
          className
        )}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"
