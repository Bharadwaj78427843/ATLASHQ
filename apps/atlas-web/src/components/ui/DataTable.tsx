import React from "react"
import { cn } from "@/lib/utils"

interface DataTableProps<T> {
  data: T[]
  columns: {
    header: string
    accessor?: keyof T | ((row: T) => React.ReactNode)
    className?: string
  }[]
  keyExtractor: (item: T) => string
  onRowClick?: (item: T) => void
  className?: string
}

export function DataTable<T>({ data, columns, keyExtractor, onRowClick, className }: DataTableProps<T>) {
  return (
    <div className={cn("w-full overflow-x-auto rounded-[var(--radius-md)] border border-[var(--color-border-subtle)] bg-[rgba(255,255,255,0.02)]", className)}>
      <table className="w-full text-sm text-left">
        <thead className="text-[var(--color-text-secondary)] border-b border-[var(--color-border-subtle)] bg-[rgba(0,0,0,0.2)]">
          <tr>
            {columns.map((col, idx) => (
              <th key={idx} className={cn("px-6 py-4 font-medium", col.className)}>
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-[var(--color-border-subtle)]">
          {data.map((row) => (
            <tr 
              key={keyExtractor(row)} 
              onClick={() => onRowClick?.(row)}
              className={cn(
                "group transition-colors hover:bg-[rgba(255,255,255,0.03)]",
                onRowClick && "cursor-pointer"
              )}
            >
              {columns.map((col, colIdx) => (
                <td key={colIdx} className={cn("px-6 py-4 text-[var(--color-text-primary)]", col.className)}>
                  {typeof col.accessor === "function" 
                    ? col.accessor(row) 
                    : col.accessor ? String(row[col.accessor] as React.ReactNode) : null}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
