import React, { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";
import { useWorkspaces } from "../hooks/useWorkspaces";
import { FormField } from "@/components/ui/FormField";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { Alert } from "@/components/ui/Alert";
import { GlassPanel } from "@/components/ui/GlassPanel";

export function WorkspaceForm({ orgId }: { orgId: string }) {
  const router = useRouter();
  const { createWorkspace } = useWorkspaces(orgId);
  const [form, setForm] = useState({ name: "", slug: "", description: "" });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      await createWorkspace(form);
      router.push(`/organizations/${orgId}`);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : "Failed to create workspace";
      setError(errorMessage);
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {error && (
        <Alert variant="error">
          {error}
        </Alert>
      )}
      
      <GlassPanel className="p-6">
        <form onSubmit={handleSubmit} noValidate className="space-y-4">
          <FormField label="Workspace Name" required>
            <Input
              id="ws-name"
              type="text"
              value={form.name}
              onChange={(e) => {
                const name = e.target.value;
                const slug = name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
                setForm(f => ({ ...f, name, slug: f.slug || slug }));
              }}
              required
              disabled={isSubmitting}
            />
          </FormField>

          <FormField label="URL Slug" required>
            <Input
              id="ws-slug"
              type="text"
              value={form.slug}
              onChange={(e) => setForm(f => ({ ...f, slug: e.target.value }))}
              required
              pattern="[a-z0-9\-]+"
              disabled={isSubmitting}
            />
            <p className="text-xs text-[var(--color-text-muted)] mt-1">
              Only lowercase letters, numbers, and hyphens.
            </p>
          </FormField>

          <FormField label="Description">
            <textarea
              id="ws-desc"
              className="w-full h-24 bg-[rgba(0,0,0,0.2)] border border-[var(--color-border-subtle)] rounded-[var(--radius-sm)] px-3 py-2 text-sm focus:outline-none focus:border-[var(--color-primary-base)] transition-colors resize-y"
              value={form.description}
              onChange={(e) => setForm(f => ({ ...f, description: e.target.value }))}
              rows={3}
              disabled={isSubmitting}
            />
          </FormField>

          <div className="pt-4 flex justify-end gap-3">
            <Button
              type="button"
              variant="secondary"
              onClick={() => router.push(`/organizations/${orgId}`)}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              disabled={isSubmitting || !form.name || !form.slug}
            >
              {isSubmitting ? <span className="spinner-ring" /> : "Create Workspace"}
            </Button>
          </div>
        </form>
      </GlassPanel>
    </div>
  );
}
