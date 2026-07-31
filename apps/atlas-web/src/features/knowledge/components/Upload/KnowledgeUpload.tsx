"use client";

import React, { useState } from "react";
import { UploadCloud } from "lucide-react";
import { GlassPanel } from "@/components/ui/GlassPanel";
import { Button } from "@/components/ui/Button";

interface KnowledgeUploadProps {
  onUpload: (file: File) => Promise<void>;
  disabled?: boolean;
}

export function KnowledgeUpload({ onUpload, disabled = false }: KnowledgeUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!file) {
      return;
    }

    setBusy(true);
    try {
      await onUpload(file);
      setFile(null);
    } finally {
      setBusy(false);
    }
  };

  return (
    <GlassPanel className="p-6">
      <div className="flex items-center gap-2 mb-4">
        <UploadCloud className="w-4 h-4 text-[var(--color-primary-light)]" />
        <h3 className="text-sm font-semibold">Upload Knowledge</h3>
      </div>

      <form onSubmit={submit} className="space-y-3">
        <input
          type="file"
          onChange={(event) => setFile(event.target.files?.[0] ?? null)}
          disabled={disabled || busy}
          className="w-full text-sm"
        />
        <Button type="submit" className="w-full" disabled={disabled || busy || !file}>
          {busy ? <span className="spinner-ring" /> : "Upload"}
        </Button>
      </form>
    </GlassPanel>
  );
}
