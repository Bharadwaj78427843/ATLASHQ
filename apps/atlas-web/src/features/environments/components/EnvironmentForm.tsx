import React, { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";
import { useEnvironments } from "../hooks/useEnvironments";
import { FormField } from "@/components/ui/FormField";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { Alert } from "@/components/ui/Alert";
import { GlassPanel } from "@/components/ui/GlassPanel";
import { EnvironmentType } from "../types";

export function EnvironmentForm({ orgId, workspaceId, projectId }: { orgId: string, workspaceId: string, projectId: string }) {
  const router = useRouter();
  const { createEnvironment } = useEnvironments(workspaceId, projectId);
  const [form, setForm] = useState<{name: string, type: EnvironmentType}>({ name: "", type: "DEVELOPMENT" });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      await createEnvironment(form);
      router.push(`/organizations/${orgId}/workspaces/${workspaceId}/projects/${projectId}`);
    } catch (err: any) {
      setError(err.message || "Failed to create environment");
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
          <FormField label="Environment Name" required>
            <Input
              id="env-name"
              type="text"
              value={form.name}
              onChange={(e) => setForm(f => ({ ...f, name: e.target.value }))}
              required
              disabled={isSubmitting}
            />
          </FormField>

          <FormField label="Environment Type" required>
            <select
              id="env-type"
              className="w-full bg-[rgba(0,0,0,0.2)] border border-[var(--color-border-subtle)] rounded-[var(--radius-sm)] px-3 py-2 text-sm focus:outline-none focus:border-[var(--color-primary-base)] transition-colors"
              value={form.type}
              onChange={(e) => setForm(f => ({ ...f, type: e.target.value as EnvironmentType }))}
              disabled={isSubmitting}
            >
              <option value="DEVELOPMENT">Development</option>
              <option value="PREVIEW">Preview</option>
              <option value="STAGING">Staging</option>
              <option value="PRODUCTION">Production</option>
            </select>
          </FormField>

          <div className="pt-4 flex justify-end gap-3">
            <Button
              type="button"
              variant="secondary"
              onClick={() => router.push(`/organizations/${orgId}/workspaces/${workspaceId}/projects/${projectId}`)}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              disabled={isSubmitting || !form.name}
            >
              {isSubmitting ? <span className="spinner-ring" /> : "Create Environment"}
            </Button>
          </div>
        </form>
      </GlassPanel>
    </div>
  );
}
