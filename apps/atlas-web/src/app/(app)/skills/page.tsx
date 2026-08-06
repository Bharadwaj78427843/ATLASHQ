"use client";

import React, { useEffect, useMemo, useState } from "react";
import { AlertTriangle, Code2, Download, RefreshCw, Rocket, ShieldCheck, Trash2 } from "lucide-react";
import { PageLayout } from "@/components/layout/PageLayout";
import { PageHeader } from "@/components/ui/PageHeader";
import { GlassPanel } from "@/components/ui/GlassPanel";
import { SkeletonLoader } from "@/components/ui/SkeletonLoader";
import { ErrorState } from "@/components/ui/ErrorState";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { aiApi, SkillExecutionResult, SkillPackage, SkillSummary } from "@/features/ai";

function formatJson(value: unknown): string {
  return JSON.stringify(value, null, 2);
}

export default function SkillsPage() {
  const [skills, setSkills] = useState<SkillSummary[]>([]);
  const [selectedSkillId, setSelectedSkillId] = useState<string | null>(null);
  const [selectedSkill, setSelectedSkill] = useState<SkillPackage | null>(null);
  const [schema, setSchema] = useState<Record<string, unknown> | null>(null);
  const [prompt, setPrompt] = useState("Prepare a release-readiness assessment for Sprint 9.");
  const [workspaceId, setWorkspaceId] = useState("");
  const [execution, setExecution] = useState<SkillExecutionResult | null>(null);
  const [validationMessage, setValidationMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [busyAction, setBusyAction] = useState<string | null>(null);

  const selectedSummary = useMemo(
    () => skills.find((skill) => skill.registry_entry.id === selectedSkillId) ?? null,
    [selectedSkillId, skills],
  );

  const loadSkills = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await aiApi.listSkills();
      const nextSkills = response.skills ?? [];
      setSkills(nextSkills);
      setSelectedSkillId((current) => {
        if (current && nextSkills.some((skill) => skill.registry_entry.id === current)) {
          return current;
        }
        return nextSkills[0]?.registry_entry.id ?? null;
      });
      if (!nextSkills.length) {
        setSelectedSkill(null);
        setSchema(null);
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let cancelled = false;

    const bootstrap = async () => {
      try {
        const response = await aiApi.listSkills();
        if (cancelled) {
          return;
        }

        const nextSkills = response.skills ?? [];
        setSkills(nextSkills);
        setSelectedSkillId((current) => {
          if (current && nextSkills.some((skill) => skill.registry_entry.id === current)) {
            return current;
          }
          return nextSkills[0]?.registry_entry.id ?? null;
        });

        if (!nextSkills.length) {
          setSelectedSkill(null);
          setSchema(null);
        }
      } catch (err: unknown) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : String(err));
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    void bootstrap();

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!selectedSkillId) {
      return;
    }

    let cancelled = false;

    const load = async () => {
      setBusyAction("loading");
      setError(null);
      try {
        const [detail, loadedSchema] = await Promise.all([
          aiApi.getSkill(selectedSkillId),
          aiApi.getSkillSchema(selectedSkillId),
        ]);
        if (cancelled) {
          return;
        }

        setSelectedSkill(detail.skill);
        setSchema(loadedSchema);
        setValidationMessage(null);
        setExecution(null);
      } catch (err: unknown) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : String(err));
        }
      } finally {
        if (!cancelled) {
          setBusyAction(null);
        }
      }
    };

    void load();

    return () => {
      cancelled = true;
    };
  }, [selectedSkillId]);

  const runAction = async (action: string, callback: () => Promise<void>) => {
    setBusyAction(action);
    setError(null);
    try {
      await callback();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusyAction(null);
    }
  };

  const handleValidate = async () => {
    if (!selectedSkillId) {
      return;
    }
    await runAction("validate", async () => {
      const response = await aiApi.validateSkill(selectedSkillId);
      setValidationMessage(response.valid ? `Skill ${response.skill_id} validated successfully.` : `Validation failed for ${response.skill_id}.`);
    });
  };

  const handleExecute = async () => {
    if (!selectedSkillId || !prompt.trim()) {
      return;
    }
    await runAction("execute", async () => {
      const response = await aiApi.executeSkill(selectedSkillId, {
        prompt: prompt.trim(),
        workspace_id: workspaceId.trim() || undefined,
        policy_context: { p0_defects: 0, p1_defects: 0 },
        metadata: { source: "skills-page" },
        request_metadata: { source: "atlas-web" },
      });
      setExecution(response);
    });
  };

  const handleReload = async () => {
    await runAction("reload", async () => {
      await aiApi.reloadSkills();
      await loadSkills();
    });
  };

  const handleInstall = async () => {
    if (!selectedSummary) {
      return;
    }
    await runAction("install", async () => {
      await aiApi.installSkill(selectedSummary.registry_entry);
      await loadSkills();
    });
  };

  const handleUninstall = async () => {
    if (!selectedSkillId) {
      return;
    }
    if (!window.confirm(`Remove skill ${selectedSkillId}?`)) {
      return;
    }
    await runAction("uninstall", async () => {
      await aiApi.uninstallSkill(selectedSkillId);
      await loadSkills();
    });
  };

  if (loading && !skills.length) {
    return (
      <PageLayout maxWidth="7xl">
        <PageHeader title="Skills" subtitle="Browse, validate, and execute Atlas skill packages." />
        <SkeletonLoader lines={10} />
      </PageLayout>
    );
  }

  if (error && !skills.length) {
    return (
      <PageLayout maxWidth="7xl">
        <PageHeader title="Skills" subtitle="Browse, validate, and execute Atlas skill packages." />
        <ErrorState error={error} onRetry={loadSkills} />
      </PageLayout>
    );
  }

  return (
    <PageLayout maxWidth="7xl">
      <PageHeader
        title="Skills Runtime"
        subtitle="One runtime for browse, validate, execute, and registry operations."
      >
        <Button variant="secondary" onClick={() => void handleReload()} disabled={busyAction !== null}>
          <RefreshCw className={busyAction === "reload" ? "mr-2 h-4 w-4 animate-spin" : "mr-2 h-4 w-4"} />
          Reload
        </Button>
        <Button variant="secondary" onClick={() => void handleValidate()} disabled={!selectedSkillId || busyAction !== null}>
          <ShieldCheck className="mr-2 h-4 w-4" />
          Validate
        </Button>
        <Button onClick={() => void handleExecute()} disabled={!selectedSkillId || busyAction !== null || !prompt.trim()}>
          <Rocket className="mr-2 h-4 w-4" />
          Execute
        </Button>
      </PageHeader>

      {error ? (
        <div className="mb-6">
          <ErrorState error={error} onRetry={loadSkills} />
        </div>
      ) : null}

      {validationMessage ? (
        <div className="mb-6 rounded-[var(--radius-md)] border border-[rgba(34,197,94,0.25)] bg-[rgba(34,197,94,0.08)] px-4 py-3 text-sm text-[var(--color-text-primary)]">
          <div className="flex items-center gap-2">
            <ShieldCheck className="h-4 w-4 text-[var(--color-accent-green)]" />
            {validationMessage}
          </div>
        </div>
      ) : null}

      <div className="grid gap-6 xl:grid-cols-[320px_minmax(0,1fr)]">
        <GlassPanel className="p-4">
          <div className="flex items-center justify-between gap-3 mb-4">
            <div>
              <h2 className="text-sm font-semibold text-[var(--color-text-primary)]">Installed Skills</h2>
              <p className="text-xs text-[var(--color-text-secondary)]">Registry-backed packages discovered from `.ai/skills`.</p>
            </div>
            <Button variant="ghost" size="sm" onClick={() => void handleReload()} disabled={busyAction !== null}>
              <RefreshCw className={busyAction === "reload" ? "mr-2 h-4 w-4 animate-spin" : "mr-2 h-4 w-4"} />
              Refresh
            </Button>
          </div>

          <div className="space-y-3">
            {skills.map((item) => {
              const active = item.registry_entry.id === selectedSkillId;
              const status = item.valid ? "success" : "error";
              return (
                <button
                  key={item.registry_entry.id}
                  type="button"
                  onClick={() => setSelectedSkillId(item.registry_entry.id)}
                  className={`w-full rounded-[var(--radius-md)] border p-4 text-left transition-colors ${active ? "border-[rgba(124,58,237,0.45)] bg-[rgba(124,58,237,0.12)]" : "border-[var(--color-border-subtle)] bg-[rgba(255,255,255,0.02)] hover:bg-[rgba(255,255,255,0.04)]"}`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="font-medium text-[var(--color-text-primary)]">{item.skill?.display_name ?? item.registry_entry.id}</h3>
                        {item.registry_entry.default ? <StatusBadge status="info" label="default" /> : null}
                      </div>
                      <p className="mt-1 text-xs text-[var(--color-text-secondary)]">{item.skill?.description ?? item.error ?? item.registry_entry.path}</p>
                    </div>
                    <StatusBadge status={status} label={item.valid ? "ready" : "invalid"} />
                  </div>
                  <div className="mt-3 flex flex-wrap gap-2 text-[11px] text-[var(--color-text-muted)]">
                    <span>{item.registry_entry.version ?? item.skill?.version ?? "unknown"}</span>
                    <span>|</span>
                    <span>{item.skill?.workflow.length ?? 0} steps</span>
                    <span>|</span>
                    <span>{item.skill?.tools.length ?? 0} tools</span>
                  </div>
                </button>
              );
            })}
            {!skills.length ? (
              <div className="rounded-[var(--radius-md)] border border-dashed border-[var(--color-border-subtle)] p-6 text-sm text-[var(--color-text-secondary)]">
                No skills found in the registry.
              </div>
            ) : null}
          </div>
        </GlassPanel>

        <div className="space-y-6">
          <GlassPanel className="p-5">
            <div className="flex items-start justify-between gap-4">
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="text-lg font-semibold text-[var(--color-text-primary)]">{selectedSkill?.display_name ?? selectedSummary?.skill?.display_name ?? selectedSkillId ?? "Select a skill"}</h2>
                  {selectedSummary?.registry_entry.default ? <StatusBadge status="info" label="default" /> : null}
                </div>
                <p className="mt-1 text-sm text-[var(--color-text-secondary)]">
                  {selectedSkill?.description ?? selectedSummary?.skill?.description ?? "Choose a skill to inspect its contract, schema, and execution trace."}
                </p>
              </div>
              <div className="flex gap-2">
                <Button variant="secondary" size="sm" onClick={() => void handleInstall()} disabled={!selectedSummary || busyAction !== null}>
                  <Download className="mr-2 h-4 w-4" />
                  Install
                </Button>
                <Button variant="danger" size="sm" onClick={() => void handleUninstall()} disabled={!selectedSkillId || busyAction !== null}>
                  <Trash2 className="mr-2 h-4 w-4" />
                  Uninstall
                </Button>
              </div>
            </div>

            <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              <div className="rounded-[var(--radius-md)] border border-[var(--color-border-subtle)] bg-[rgba(255,255,255,0.02)] p-4">
                <p className="text-xs uppercase tracking-wide text-[var(--color-text-muted)]">Version</p>
                <p className="mt-2 text-sm text-[var(--color-text-primary)]">{selectedSkill?.version ?? selectedSummary?.registry_entry.version ?? "Unknown"}</p>
              </div>
              <div className="rounded-[var(--radius-md)] border border-[var(--color-border-subtle)] bg-[rgba(255,255,255,0.02)] p-4">
                <p className="text-xs uppercase tracking-wide text-[var(--color-text-muted)]">Owners</p>
                <p className="mt-2 text-sm text-[var(--color-text-primary)]">{selectedSkill?.owners?.join(", ") ?? "Unknown"}</p>
              </div>
              <div className="rounded-[var(--radius-md)] border border-[var(--color-border-subtle)] bg-[rgba(255,255,255,0.02)] p-4">
                <p className="text-xs uppercase tracking-wide text-[var(--color-text-muted)]">Workflow Steps</p>
                <p className="mt-2 text-sm text-[var(--color-text-primary)]">{selectedSkill?.workflow?.length ?? 0}</p>
              </div>
              <div className="rounded-[var(--radius-md)] border border-[var(--color-border-subtle)] bg-[rgba(255,255,255,0.02)] p-4">
                <p className="text-xs uppercase tracking-wide text-[var(--color-text-muted)]">Tool Permissions</p>
                <p className="mt-2 text-sm text-[var(--color-text-primary)]">{selectedSkill?.tools?.length ?? 0} allowed tools</p>
              </div>
            </div>
          </GlassPanel>

          <div className="grid gap-6 xl:grid-cols-2">
            <GlassPanel className="p-5">
              <div className="flex items-center gap-2 mb-4">
                <Code2 className="h-4 w-4 text-[var(--color-primary-light)]" />
                <h3 className="text-sm font-semibold">Execution Input</h3>
              </div>
              <div className="space-y-4">
                <label className="block space-y-2 text-sm">
                  <span className="text-[var(--color-text-secondary)]">Workspace ID</span>
                  <Input value={workspaceId} onChange={(event) => setWorkspaceId(event.target.value)} placeholder="workspace-123" />
                </label>
                <label className="block space-y-2 text-sm">
                  <span className="text-[var(--color-text-secondary)]">Prompt</span>
                  <textarea
                    value={prompt}
                    onChange={(event) => setPrompt(event.target.value)}
                    rows={8}
                    className="w-full rounded-[var(--radius-sm)] border border-[var(--color-border-subtle)] bg-[var(--color-panel)] px-3 py-2 text-sm text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)] focus:outline-none focus:ring-1 focus:ring-[var(--color-primary-base)]"
                    placeholder="Describe the task for this skill"
                  />
                </label>
              </div>
            </GlassPanel>

            <GlassPanel className="p-5">
              <div className="flex items-center gap-2 mb-4">
                <AlertTriangle className="h-4 w-4 text-[var(--color-primary-light)]" />
                <h3 className="text-sm font-semibold">Runtime State</h3>
              </div>
              <div className="space-y-4 text-sm text-[var(--color-text-secondary)]">
                <div>
                  <p className="text-xs uppercase tracking-wide text-[var(--color-text-muted)]">Registry Path</p>
                  <p className="mt-1 break-all text-[var(--color-text-primary)]">{selectedSummary?.registry_entry.path ?? "Unknown"}</p>
                </div>
                <div>
                  <p className="text-xs uppercase tracking-wide text-[var(--color-text-muted)]">Validation</p>
                  <p className="mt-1 text-[var(--color-text-primary)]">{validationMessage ?? "Run validation to confirm the package and its contracts."}</p>
                </div>
                <div>
                  <p className="text-xs uppercase tracking-wide text-[var(--color-text-muted)]">Execution</p>
                  <p className="mt-1 text-[var(--color-text-primary)]">{execution ? `${execution.status} - ${execution.execution_id}` : "No execution yet."}</p>
                </div>
              </div>
            </GlassPanel>
          </div>

          <div className="grid gap-6 xl:grid-cols-2">
            <GlassPanel className="p-5">
              <h3 className="mb-4 text-sm font-semibold flex items-center gap-2">
                <ShieldCheck className="h-4 w-4 text-[var(--color-primary-light)]" />
                Schema Bundle
              </h3>
              <pre className="max-h-[520px] overflow-auto rounded-[var(--radius-md)] border border-[var(--color-border-subtle)] bg-[rgba(0,0,0,0.3)] p-4 text-xs leading-6 text-[var(--color-text-secondary)]">
                {formatJson(schema ?? {})}
              </pre>
            </GlassPanel>

            <GlassPanel className="p-5">
              <h3 className="mb-4 text-sm font-semibold flex items-center gap-2">
                <Rocket className="h-4 w-4 text-[var(--color-primary-light)]" />
                Latest Execution
              </h3>
              <pre className="max-h-[520px] overflow-auto rounded-[var(--radius-md)] border border-[var(--color-border-subtle)] bg-[rgba(0,0,0,0.3)] p-4 text-xs leading-6 text-[var(--color-text-secondary)]">
                {formatJson(execution ?? {})}
              </pre>
            </GlassPanel>
          </div>
        </div>
      </div>
    </PageLayout>
  );
}
