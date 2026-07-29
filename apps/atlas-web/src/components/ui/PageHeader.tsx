import React from "react"
import Link from "next/link"
import { ArrowLeft } from "lucide-react"

interface PageHeaderProps {
  title: string
  subtitle?: string
  backLink?: {
    href: string
    label: string
  }
  children?: React.ReactNode // For action buttons
}

export function PageHeader({ title, subtitle, backLink, children }: PageHeaderProps) {
  return (
    <div className="mb-8">
      {backLink && (
        <Link 
          href={backLink.href} 
          className="inline-flex items-center gap-2 text-sm text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] transition-colors mb-4"
        >
          <ArrowLeft className="w-4 h-4" />
          {backLink.label}
        </Link>
      )}
      
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-[var(--color-text-primary)]">{title}</h1>
          {subtitle && (
            <p className="mt-1.5 text-sm text-[var(--color-text-secondary)] max-w-2xl">
              {subtitle}
            </p>
          )}
        </div>
        
        {children && (
          <div className="flex items-center gap-3 shrink-0">
            {children}
          </div>
        )}
      </div>
    </div>
  )
}
