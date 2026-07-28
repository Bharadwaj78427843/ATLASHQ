"use client";

/**
 * src/app/organizations/new/page.tsx
 *
 * ATLAS-011 — Create Organization page.
 * Form with frontend validation reflecting backend schemas.
 */
import React, { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useCreateOrganization } from "@/hooks/useOrganizations";

export default function CreateOrganizationPage() {
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

    // Basic frontend validation matching Pydantic
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
      // Error is handled by hook and displayed below
    }
  }

  const displayError = validationError || error;

  return (
    <div style={{ maxWidth: "600px", margin: "0 auto" }}>
      <div style={{ marginBottom: "32px" }}>
        <Link href="/organizations" style={{ color: "var(--text-secondary)", textDecoration: "none", fontSize: "14px", display: "inline-block", marginBottom: "16px" }}>
          ← Back to Organizations
        </Link>
        <h1 className="hero-title" style={{ fontSize: "28px", marginBottom: "8px" }}>Create Organization</h1>
        <p className="hero-subtitle">Set up a new workspace for your team.</p>
      </div>

      {displayError && (
        <div className="alert alert-error" role="alert">
          {displayError}
        </div>
      )}

      <div className="profile-card">
        <form onSubmit={handleSubmit} noValidate>
          <div className="form-group">
            <label className="form-label" htmlFor="org-name">Organization Name *</label>
            <input
              id="org-name"
              type="text"
              className="form-input"
              placeholder="Acme Corp"
              value={form.name}
              onChange={onChange("name")}
              required
              maxLength={120}
              disabled={isSubmitting}
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="org-slug">URL Slug *</label>
            <input
              id="org-slug"
              type="text"
              className="form-input"
              placeholder="acme-corp"
              value={form.slug}
              onChange={onChange("slug")}
              required
              minLength={3}
              maxLength={80}
              disabled={isSubmitting}
            />
            <p style={{ fontSize: "12px", color: "var(--text-muted)", marginTop: "4px" }}>
              Unique identifier used in URLs. Lowercase letters, numbers, and hyphens only.
            </p>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="org-website">Website URL</label>
            <input
              id="org-website"
              type="url"
              className="form-input"
              placeholder="https://acme.com"
              value={form.website}
              onChange={onChange("website")}
              maxLength={500}
              disabled={isSubmitting}
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="org-desc">Description</label>
            <textarea
              id="org-desc"
              className="form-input"
              placeholder="What does your organization do?"
              value={form.description}
              onChange={onChange("description")}
              maxLength={1000}
              rows={4}
              style={{ resize: "vertical" }}
              disabled={isSubmitting}
            />
          </div>

          <div style={{ marginTop: "32px", display: "flex", justifyContent: "flex-end", gap: "12px" }}>
            <button
              type="button"
              className="btn-ghost"
              onClick={() => router.push("/organizations")}
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn-primary"
              style={{ width: "auto" }}
              disabled={isSubmitting || !form.name || !form.slug}
            >
              {isSubmitting ? <span className="btn-spinner" /> : "Create Organization"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
