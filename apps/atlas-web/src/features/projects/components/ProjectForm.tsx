import React, { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";
import { useProjects } from "../hooks/useProjects";
import { FormField } from "@/components/ui/FormField";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { Alert } from "@/components/ui/Alert";
import { GlassPanel } from "@/components/ui/GlassPanel";

export function ProjectForm({ orgId, workspaceId }: { orgId: string, workspaceId: string }) {
  const router = useRouter();
  const { createProject } = useProjects(workspaceId);
  const [form, setForm] = useState({ name: "", description: "" });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      await createProject(form);
      router.push(`/organizations/${orgId}/workspaces/${workspaceId}`);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : "Failed to create project";
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
          <FormField label="Project Name" required>
            <Input
              id="project-name"
              type="text"
              value={form.name}
              onChange={(e) => setForm(f => ({ ...f, name: e.target.value }))}
              required
              disabled={isSubmitting}
            />
          </FormField>

          <FormField label="Description">
            <textarea
              id="project-desc"
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
              onClick={() => router.push(`/organizations/${orgId}/workspaces/${workspaceId}`)}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              disabled={isSubmitting || !form.name}
            >
              {isSubmitting ? <span className="spinner-ring" /> : "Create Project"}
            </Button>
          </div>
        </form>
      </GlassPanel>
    </div>
  );
}
