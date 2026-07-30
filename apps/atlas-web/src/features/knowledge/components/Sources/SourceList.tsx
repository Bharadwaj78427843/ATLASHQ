import React from "react";
import { KnowledgeSource } from "../../types";
import { DataTable } from "@/components/ui/DataTable";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { FileText, GitBranch, Globe, Database, Trash2 } from "lucide-react";

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const minutes = Math.floor(diff / 60000);
  if (minutes < 1) return "just now";
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

function SourceIcon({ type }: { type: string }) {
  switch (type) {
    case "github": return <GitBranch className="w-4 h-4 text-gray-400" />;
    case "web":    return <Globe className="w-4 h-4 text-green-500" />;
    case "document": return <FileText className="w-4 h-4 text-blue-500" />;
    default:       return <Database className="w-4 h-4 text-purple-500" />;
  }
}

interface SourceListProps {
  sources: KnowledgeSource[];
  onDelete?: (id: string) => void;
}

export function SourceList({ sources, onDelete }: SourceListProps) {
  const columns = [
    {
      header: "Name",
      accessor: (source: KnowledgeSource) => (
        <div className="flex items-center gap-3">
          <SourceIcon type={source.source_type} />
          <span className="font-medium text-[var(--color-text-primary)]">{source.name}</span>
        </div>
      ),
    },
    {
      header: "Status",
      accessor: (source: KnowledgeSource) => (
        <StatusBadge status={source.status as React.ComponentProps<typeof StatusBadge>["status"]} label={source.status.replace("_", " ")} />
      ),
    },
    {
      header: "Created",
      accessor: (source: KnowledgeSource) => (
        <span className="text-[var(--color-text-secondary)]">
          {source.created_at ? timeAgo(source.created_at) : "Unknown"}
        </span>
      ),
    },
    ...(onDelete
      ? [
          {
            header: "",
            className: "text-right w-12",
            accessor: (source: KnowledgeSource) => (
              <button
                onClick={() => onDelete(source.id)}
                className="p-2 text-[var(--color-text-muted)] hover:text-red-500 hover:bg-red-500/10 rounded-md transition-colors"
                title="Delete"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            ),
          },
        ]
      : []),
  ];

  return (
    <DataTable
      columns={columns}
      data={sources}
      keyExtractor={(item) => item.id}
    />
  );
}
