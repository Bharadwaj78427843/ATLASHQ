"use client";

import React, { useState, useEffect } from "react";
import { aiApi, AIProvider } from "@/features/ai/api";
import { PageHeader } from "@/components/ui/PageHeader";
import { PageLayout } from "@/components/layout/PageLayout";
import { SkeletonLoader } from "@/components/ui/SkeletonLoader";
import { ErrorState } from "@/components/ui/ErrorState";
import { Settings, CheckCircle2, XCircle } from "lucide-react";

export default function AISettingsPage() {
  const [providers, setProviders] = useState<AIProvider[]>([]);
  const [health, setHealth] = useState<{ status?: string; sdk?: string } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSettings = async () => {
    setLoading(true);
    setError(null);
    try {
      const [providersRes, healthRes] = await Promise.all([
        aiApi.getProviders(),
        aiApi.getHealth()
      ]);
      setProviders(providersRes.providers || []);
      setHealth(healthRes);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : String(err);
      setError("Failed to load AI settings. " + errorMessage);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void fetchSettings();
  }, []);

  return (
    <PageLayout maxWidth="3xl">
      <PageHeader 
        title="AI Settings" 
        subtitle="Manage AI providers, models, and platform health."
      />

      {error ? (
        <ErrorState error={error} onRetry={fetchSettings} />
      ) : loading ? (
        <SkeletonLoader lines={8} />
      ) : (
        <div className="space-y-8">
          {/* Health Status */}
          <section className="bg-[var(--color-panel)] border border-[var(--color-border-subtle)] rounded-[var(--radius-lg)] p-6">
            <h3 className="text-lg font-semibold text-[var(--color-text-primary)] mb-4 flex items-center gap-2">
              <Settings className="w-5 h-5 text-[var(--color-text-muted)]" />
              Platform Health
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="p-4 rounded-[var(--radius-md)] bg-[rgba(255,255,255,0.02)] border border-[var(--color-border-subtle)]">
                <p className="text-sm text-[var(--color-text-muted)] mb-1">Status</p>
                <div className="flex items-center gap-2 text-lg font-medium text-[var(--color-text-primary)] capitalize">
                  {health?.status === "ok" ? (
                    <CheckCircle2 className="w-5 h-5 text-green-500" />
                  ) : (
                    <XCircle className="w-5 h-5 text-red-500" />
                  )}
                  {health?.status || "Unknown"}
                </div>
              </div>
              <div className="p-4 rounded-[var(--radius-md)] bg-[rgba(255,255,255,0.02)] border border-[var(--color-border-subtle)]">
                <p className="text-sm text-[var(--color-text-muted)] mb-1">AI Engine</p>
                <p className="text-lg font-medium text-[var(--color-text-primary)]">
                  {health?.sdk || "AtlasRuntime"}
                </p>
              </div>
            </div>
          </section>

          {/* Providers List */}
          <section className="bg-[var(--color-panel)] border border-[var(--color-border-subtle)] rounded-[var(--radius-lg)] p-6">
            <h3 className="text-lg font-semibold text-[var(--color-text-primary)] mb-4 flex items-center gap-2">
              <Settings className="w-5 h-5 text-[var(--color-text-muted)]" />
              AI Providers
            </h3>
            
            {providers.length === 0 ? (
              <p className="text-[var(--color-text-muted)]">No providers configured.</p>
            ) : (
              <div className="space-y-4">
                {providers.map((p, idx) => (
                  <div key={idx} className="p-4 rounded-[var(--radius-md)] bg-[rgba(255,255,255,0.02)] border border-[var(--color-border-subtle)] flex items-center justify-between">
                    <div>
                      <h4 className="font-medium text-[var(--color-text-primary)] capitalize">{p.name} <span className="text-[var(--color-text-muted)] text-sm ml-2">({p.category})</span></h4>
                      <p className="text-sm text-[var(--color-text-secondary)] mt-1">{p.health_message}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      {p.is_active ? (
                        <span className="px-2 py-1 bg-green-500/10 border border-green-500/20 text-green-500 rounded-full text-xs font-medium flex items-center gap-1">
                          <CheckCircle2 className="w-3 h-3" /> Active
                        </span>
                      ) : (
                        <span className="px-2 py-1 bg-gray-500/10 border border-gray-500/20 text-gray-500 rounded-full text-xs font-medium">
                          Inactive
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
        </div>
      )}
    </PageLayout>
  );
}
