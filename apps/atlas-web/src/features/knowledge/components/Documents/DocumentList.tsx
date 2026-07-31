import React from "react";
import { FileText } from "lucide-react";
import { EmptyState } from "@/components/ui/EmptyState";
import { DataTable } from "@/components/ui/DataTable";
import { KnowledgeSource } from "../../types";

interface DocumentListProps {
  documents: KnowledgeSource[];
}

export function DocumentList({ documents }: DocumentListProps) {
  const sourceDocuments = documents.filter((source) => source.source_type.toLowerCase() !== "repository");

  if (sourceDocuments.length === 0) {
    return (
      <EmptyState
        icon={FileText}
        title="No documents uploaded"
        description="Upload your first document to begin building searchable workspace knowledge."
      />
    );
  }

  return (
    <DataTable
      data={sourceDocuments}
      keyExtractor={(document) => document.id}
      columns={[
        {
          header: "Name",
          accessor: (document: KnowledgeSource) => (
            <span className="text-sm font-medium text-[var(--color-text-primary)]">{document.name}</span>
          ),
        },
        {
          header: "Type",
          accessor: (document: KnowledgeSource) => (
            <span className="text-sm text-[var(--color-text-secondary)] capitalize">{document.source_type}</span>
          ),
        },
        {
          header: "Status",
          accessor: (document: KnowledgeSource) => (
            <span className="text-xs uppercase text-[var(--color-text-muted)]">{document.status}</span>
          ),
        },
      ]}
    />
  );
}
