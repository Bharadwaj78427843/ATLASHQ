"use client";

import React, { useState } from "react";
import { GitBranch } from "lucide-react";
import { GlassPanel } from "@/components/ui/GlassPanel";
import { FormField } from "@/components/ui/FormField";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";

interface RepositoryConnectProps {
  onConnect: (payload: { repositoryUrl: string; branch: string }) => Promise<void>;
  disabled?: boolean;
}

export function RepositoryConnect({ onConnect, disabled = false }: RepositoryConnectProps) {
  const [repositoryUrl, setRepositoryUrl] = useState("");
  const [branch, setBranch] = useState("main");
  const [busy, setBusy] = useState(false);

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!repositoryUrl.trim() || !branch.trim()) {
      return;
    }

    setBusy(true);
    try {
      await onConnect({ repositoryUrl: repositoryUrl.trim(), branch: branch.trim() });
      setRepositoryUrl("");
      setBranch("main");
    } finally {
      setBusy(false);
    }
  };

  return (
    <GlassPanel className="p-5">
      <div className="flex items-center gap-2 mb-4">
        <GitBranch className="w-4 h-4 text-[var(--color-primary-light)]" />
        <h3 className="text-sm font-semibold">Connect Repository</h3>
      </div>

      <form onSubmit={submit} className="space-y-3">
        <FormField label="GitHub URL" required>
          <Input
            placeholder="https://github.com/owner/repository"
            value={repositoryUrl}
            onChange={(event) => setRepositoryUrl(event.target.value)}
            disabled={disabled || busy}
            required
          />
        </FormField>
        <FormField label="Branch" required>
          <Input
            placeholder="main"
            value={branch}
            onChange={(event) => setBranch(event.target.value)}
            disabled={disabled || busy}
            required
          />
        </FormField>
        <Button type="submit" className="w-full" disabled={disabled || busy || !repositoryUrl.trim() || !branch.trim()}>
          {busy ? <span className="spinner-ring" /> : "Connect"}
        </Button>
      </form>
    </GlassPanel>
  );
}
