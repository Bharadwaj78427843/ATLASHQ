import React, { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";
import { useCreateOrganization } from "../hooks/useOrganizations";
import { FormField } from "@/components/ui/FormField";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { Alert } from "@/components/ui/Alert";
import { GlassPanel } from "@/components/ui/GlassPanel";

export function OrganizationForm() {
  const router = useRouter();
  const { create, isSubmitting, error, clearError } = useCreateOrganization();

  const [form, setForm] = useState({
    name: "",
    slug: "",
    description: "",
    website: "",
  });

  const [validationError, setValidationError] = useState<string | null>(null);

  function onChange(field: keyof typeof form) {
    return (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
      setValidationError(null);
      clearError();
      let value = e.target.value;
      if (field === "slug") {
        value = value.toLowerCase().replace(/[^a-z0-9-]/g, "");
      }
      setForm((prev) => ({ ...prev, [field]: value }));
    };
  }

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setValidationError(null);

    // Basic frontend validation
    if (form.slug.length < 3) {
      setValidationError("Slug must be at least 3 characters.");
      return;
    }
    if (form.slug.startsWith("-") || form.slug.endsWith("-")) {
      setValidationError("Slug cannot start or end with a hyphen.");
      return;
    }
    if (form.website && !form.website.startsWith("http://") && !form.website.startsWith("https://")) {
      setValidationError("Website must start with http:// or https://");
      return;
    }

    try {
      const org = await create({
        name: form.name,
        slug: form.slug,
        description: form.description || undefined,
        website: form.website || undefined,
      });
      router.push(`/organizations/${org.id}`);
    } catch (err) {
      // Error is handled by hook
    }
  }

  const displayError = validationError || error;

  return (
    <div className="space-y-6">
      {displayError && (
        <Alert variant="error">
          {displayError}
        </Alert>
      )}

      <GlassPanel className="p-6">
        <form onSubmit={handleSubmit} noValidate className="space-y-4">
          <FormField label="Organization Name" required>
            <Input
              id="org-name"
              type="text"
              placeholder="Acme Corp"
              value={form.name}
              onChange={onChange("name")}
              required
              maxLength={120}
              disabled={isSubmitting}
            />
          </FormField>

          <FormField label="URL Slug" required>
            <Input
              id="org-slug"
              type="text"
              placeholder="acme-corp"
              value={form.slug}
              onChange={onChange("slug")}
              required
              minLength={3}
              maxLength={80}
              disabled={isSubmitting}
            />
            <p className="text-xs text-[var(--color-text-muted)] mt-1">
              Unique identifier used in URLs. Lowercase letters, numbers, and hyphens only.
            </p>
          </FormField>

          <FormField label="Website URL">
            <Input
              id="org-website"
              type="url"
              placeholder="https://acme.com"
              value={form.website}
              onChange={onChange("website")}
              maxLength={500}
              disabled={isSubmitting}
            />
          </FormField>

          <FormField label="Description">
            <textarea
              id="org-desc"
              className="w-full h-24 bg-[rgba(0,0,0,0.2)] border border-[var(--color-border-subtle)] rounded-[var(--radius-sm)] px-3 py-2 text-sm focus:outline-none focus:border-[var(--color-primary-base)] transition-colors resize-y"
              placeholder="What does your organization do?"
              value={form.description}
              onChange={onChange("description")}
              maxLength={1000}
              disabled={isSubmitting}
            />
          </FormField>

          <div className="pt-4 flex justify-end gap-3">
            <Button
              type="button"
              variant="secondary"
              onClick={() => router.push("/organizations")}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              disabled={isSubmitting || !form.name || !form.slug}
            >
              {isSubmitting ? <span className="spinner-ring" /> : "Create Organization"}
            </Button>
          </div>
        </form>
      </GlassPanel>
    </div>
  );
}
